from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
import os
from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from . import models

# Create your views here.

def custom_404(request, exception):
    context = get_user_profile(request)
    if context.get('is_authenticated'):
        return redirect('home')
    return redirect('login')

def get_user_profile(request):
    """
    Retorna informações do perfil do usuário logado, se houver.
    Usada em todas as views para fornecer o nome de perfil no template.
    """
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = models.UsuUsuario.objects.get(id=user_id, ativo=1, deletado=0)
            return {
                'user_id': user.id,
                'user_name': user.nome_exibicao or user.nome,
                'is_authenticated': True
            }
        except models.UsuUsuario.DoesNotExist:
            return {'user_name': '', 'is_authenticated': False}
    return {'user_name': '', 'is_authenticated': False}

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    
    username = request.POST.get('user')
    senha = request.POST.get('password')
    
    try:
        user = models.UsuUsuario.objects.get(login=username, senha=senha)
        # Configure a sessão com as informações do usuário
        request.session['user_id'] = user.id
        request.session['user_name'] = user.nome_exibicao or user.nome
        return redirect('home')
    except models.UsuUsuario.DoesNotExist:
        return render(request, 'login.html', {'error': 'Credenciais inválidas'})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redireciona para a página de login

def home(request):
    context = get_user_profile(request)
    
    try:
        # Busca o status "Aberto" ou cria caso não exista
        status_aberto, _ = models.ChStatus.objects.get_or_create(nome='Aguardando Atendimento')
        
        # Filtra os chamados abertos do usuário logado
        chamados_abertos = models.ChChamado.objects.filter(
            id_status=status_aberto,
            id_usuario__id=context['user_id'],
            deletado=0
        ).select_related(
            'id_usuario', 'id_setor', 'id_usuario_suporte', 'id_setor_suporte'
        ).prefetch_related(
            'chcategoriadochamado_set__id_categoria',
            'chcategoriadochamado_set__id_subcategoria'
        )
        
        # Processa categorias e subcategorias associadas a cada chamado
        for chamado in chamados_abertos:
            chamado.categorias = []
            for cat in chamado.chcategoriadochamado_set.all():
                categoria_nome = cat.id_categoria.nome if cat.id_categoria else "Sem categoria"
                subcategoria_nome = cat.id_subcategoria.nome if cat.id_subcategoria else "Sem subcategoria"
                chamado.categorias.append({
                    'categoria': categoria_nome,
                    'subcategoria': subcategoria_nome
                })
            
            # Caso não haja categorias associadas, adiciona um valor padrão
            if not chamado.categorias:
                chamado.categorias.append({
                    'categoria': "Sem categoria",
                    'subcategoria': "Sem subcategoria"
                })
        
        # Atualiza o contexto com os chamados abertos
        context.update({'chamados_abertos': chamados_abertos})
    
    except Exception as e:
        print(f"Erro ao carregar a página inicial: {e}")  # Log para depuração
        messages.error(request, 'Erro ao carregar os chamados abertos.')
    
    return render(request, 'home.html', context)

def get_subcategories(request):
    category_id = request.GET.get('category_id')
    # Corrigido de categoria_id para id_categoria
    subcategories = models.ChSubcategoria.objects.filter(id_categoria=category_id).values('id', 'nome')
    return JsonResponse(list(subcategories), safe=False)

def helpdesk(request):
    context = get_user_profile(request)
    
    if request.method == 'POST':
        try:
            setor_id = request.POST.get('id_setor')
            patrimonio = request.POST.get('patrimonio')
            descricao = request.POST.get('description')
            arquivos = request.FILES.getlist('arquivo')
            # Coleta categorias e subcategorias como listas
            categorias = [value for key, value in request.POST.items() if key.startswith('id_categoria_')]
            subcategorias = [value for key, value in request.POST.items() if key.startswith('id_subcategoria_')]
            
            # Valida se há pares correspondentes
            if len(categorias) != len(subcategorias):
                messages.error(request, 'O número de categorias e subcategorias não corresponde.')
                return redirect('helpdesk')
            
            # Obter ou criar o status "Aberto"
            status, _ = models.ChStatus.objects.get_or_create(nome='Aguardando Atendimento')
            
            # Obter usuário logado
            usuario = models.UsuUsuario.objects.get(id=context['user_id'], ativo=1, deletado=0)
            setor = models.UsuSetor.objects.get(id=int(setor_id))
            unidade = usuario.id_unidade
            
            # Criar chamado
            chamado = models.ChChamado.objects.create(
                id_usuario=usuario,
                id_setor=setor,
                id_unidade=unidade,
                id_usuario_suporte=usuario,
                id_setor_suporte=setor,
                id_status=status,
                prioridade=1,
                patrimonio=int(patrimonio) if patrimonio and patrimonio.strip() else None,
                descricao=descricao,
                deletado=0,
                data_cadastro=timezone.now()
            )
            
            # Criar interação
            interacao = models.ChInteracao.objects.create(
                id_usuario=usuario,
                id_chamado=chamado,
                id_status=status,
                descricao='Chamado aberto pelo usuário.',
                suporte=0,
                data_cadastro=timezone.now()
            )
            
            # Associar categorias e subcategorias
            saved_categories = False
            for cat_id, subcat_id in zip(categorias, subcategorias):
                if cat_id and subcat_id:  # Garante que ambos os IDs são válidos
                    try:
                        categoria = models.ChCategoria.objects.get(id=int(cat_id))
                        subcategoria = models.ChSubcategoria.objects.get(id=int(subcat_id))
                        models.ChCategoriaDoChamado.objects.create(
                            id_chamado=chamado,
                            id_subcategoria=subcategoria,
                            id_categoria=categoria
                        )
                        saved_categories = True
                    except (models.ChCategoria.DoesNotExist, models.ChSubcategoria.DoesNotExist):
                        messages.warning(request, f'Categoria {cat_id} ou subcategoria {subcat_id} inválida foi ignorada.')
                else:
                    messages.warning(request, 'Um par de categoria/subcategoria estava incompleto e foi ignorado.')
            
            # Verifica se pelo menos uma categoria foi salva
            if not saved_categories and categorias:
                messages.warning(request, 'Nenhuma categoria/subcategoria válida foi associada ao chamado.')
            
            # Processar arquivos
            for arquivo in arquivos:
                if arquivo.size > 35 * 1024 * 1024:
                    messages.error(request, f'O arquivo {arquivo.name} excede o tamanho máximo de 35MB.')
                    continue
                extensao = os.path.splitext(arquivo.name)[1].lower()[1:]
                extensoes_permitidas = ['jpg', 'jpeg', 'png', 'pdf', 'xls', 'xlsx', 'doc', 'docx', 'txt', 'eml', 'zip']
                if extensao not in extensoes_permitidas:
                    messages.error(request, f'O formato do arquivo {arquivo.name} não é permitido.')
                    continue
                caminho_arquivo = default_storage.save(f'chamados/{chamado.id}/{arquivo.name}', arquivo)
                models.ChArquivo.objects.create(
                    id_interacao=interacao,
                    arquivo=caminho_arquivo,
                    extensao=extensao,
                    tamanho=arquivo.size / (1024 * 1024),
                    deletado=0,
                    data_cadastro=timezone.now()
                )
            
            messages.success(request, 'Chamado aberto com sucesso!')
            return redirect('helpdesk')
        
        except (models.UsuUsuario.DoesNotExist, models.UsuSetor.DoesNotExist):
            messages.error(request, 'Usuário ou setor inválido.')
        except Exception as e:
            print(f"Erro ao abrir chamado: {e}")  # Depuração
            messages.error(request, f'Erro ao abrir chamado: {str(e)}')
        
        return redirect('helpdesk')
    
    context.update({
        'name_user': [models.UsuUsuario.objects.get(id=context['user_id'])],
        'units': models.UsuUnidade.objects.all(),
        'sectors': models.UsuSetor.objects.all(),
        'categories': models.ChCategoria.objects.all(),
        'subcategories': models.ChSubcategoria.objects.all(),
    })
    
    return render(request, 'helpdesk.html', context)

def int_chamado(request, chamado_id):
    context = get_user_profile(request)
    
    try:
        # Busca o chamado pelo ID
        chamado = models.ChChamado.objects.get(id=chamado_id, deletado=0)
        
        # Verifica se o usuário logado é o mesmo associado ao chamado
        if chamado.id_usuario.id != context['user_id']:
            messages.error(request, 'Você não tem permissão para visualizar este chamado.')
            return redirect('home')
        
        # Lida com o envio de mensagens
        if request.method == 'POST':
            mensagem = request.POST.get('mensagem')
            if mensagem:
                usuario = models.UsuUsuario.objects.get(id=context['user_id'])
                status = chamado.id_status  # Usa o status atual do chamado
                
                # Cria uma nova interação
                models.ChInteracao.objects.create(
                    id_usuario=usuario,
                    id_chamado=chamado,
                    id_status=status,
                    descricao=mensagem,
                    suporte=0,  # Define se é uma mensagem do suporte ou do usuário
                    data_cadastro=timezone.now()
                )
                messages.success(request, 'Mensagem enviada com sucesso!')
                return redirect('int_chamado', chamado_id=chamado.id)
            else:
                messages.error(request, 'A mensagem não pode estar vazia.')

        # Busca as interações relacionadas ao chamado
        interacoes = models.ChInteracao.objects.filter(
            id_chamado=chamado
        ).select_related('id_usuario', 'id_status').order_by('data_cadastro')
        
        # Atualiza o contexto com o chamado e as interações
        context.update({
            'chamado': chamado,
            'interacoes': interacoes,
            'status_chamada': chamado.id_status,  # Mostra apenas o status do chamado atual
        })
    
    except models.ChChamado.DoesNotExist:
        messages.error(request, 'Chamado não encontrado.')
        return redirect('home')
    
    return render(request, 'int_chamados.html', context)