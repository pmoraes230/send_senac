from functools import wraps
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

# Função para obter o perfil do usuário logado
def get_user_profile(request):
    """
    Retorna informações do perfil do usuário logado, se houver.
    Usada em todas as views para fornecer o nome de perfil no template.
    """
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = models.UsuUsuario.objects.select_related('id_grupo_usuario').get(id=user_id, ativo=1, deletado=0)
            return {
                'user_id': user.id,
                'user_name': user.nome_exibicao or user.nome,
                'user_role': user.id_grupo_usuario.nome,
                'is_authenticated': True
            }
        except models.UsuUsuario.DoesNotExist:
            return {'user_name': '', 'is_authenticated': False}
    return {'user_name': '', 'is_authenticated': False}

def role_required(*roles):
    """
    Decorador para verificar se o usuário pertence a um dos grupos especificados.
    """

    def decorator(view_funv):
        @wraps(view_funv)
        def _wrapped_view(request, *args, **kwargs):
            user_profile = get_user_profile(request)
            user_role = user_profile.get('user_role')

            if user_role not in roles:
                messages.error(request, 'Você não tem permissão para acessar esta página.')
                return redirect('login')
            
            return view_funv(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    
    username = request.POST.get('user')
    senha = request.POST.get('password')
    
    try:
        user = models.UsuUsuario.objects.get(login=username, senha=senha)
        request.session['user_id'] = user.id
        request.session['user_name'] = user.nome_exibicao or user.nome
        request.session['user_role'] = user.id_grupo_usuario.nome
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

@role_required('A', 'B', 'C', 'D')
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
            arquivo = request.FILES.get('arquivo')  # Obtém o arquivo enviado
            
            if mensagem:
                usuario = models.UsuUsuario.objects.get(id=context['user_id'])
                status = chamado.id_status  # Usa o status atual do chamado
                
                # Cria uma nova interação
                interacao = models.ChInteracao.objects.create(
                    id_usuario=usuario,
                    id_chamado=chamado,
                    id_status=status,
                    descricao=mensagem,
                    suporte=0,  # Define se é uma mensagem do suporte ou do usuário
                    data_cadastro=timezone.now()
                )
                
                # Se um arquivo foi enviado, cria um registro em ChArquivo
                if arquivo:
                    extensao = os.path.splitext(arquivo.name)[1].lower()[1:]
                    caminho_arquivo = default_storage.save(f'chamados/{chamado.id}/{arquivo.name}', arquivo)
                    models.ChArquivo.objects.create(
                        id_interacao=interacao,
                        arquivo=caminho_arquivo,
                        extensao=extensao,
                        tamanho=arquivo.size / (1024 * 1024),  # Tamanho em MB
                        deletado=0,
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

        # Busca os arquivos relacionados às interações do chamado
        arquivos = models.ChArquivo.objects.filter(
            id_interacao__id_chamado=chamado,
            deletado=0
        )
        
        # Atualiza o contexto com o chamado, interações e arquivos
        context.update({
            'chamado': chamado,
            'interacoes': interacoes,
            'arquivos': arquivos,
            'status_chamada': chamado.id_status,  # Status do chamado
            'categorias': chamado.chcategoriadochamado_set.all(),  # Categorias e subcategorias
            'solicitante': chamado.id_usuario,  # Usuário que abriu o chamado
            'patrimonio': chamado.patrimonio,  # Patrimônio associado ao chamado
            'data_cadastro': chamado.data_cadastro,  # Data de cadastro do chamado
            'tecnico_responsavel': chamado.id_usuario_suporte,  # Técnico responsável
            'cadastrado_por': chamado.id_usuario,  # Usuário que cadastrou o chamado
        })
    
    except models.ChChamado.DoesNotExist:
        messages.error(request, 'Chamado não encontrado.')
        return redirect('home')
    
    return render(request, 'int_chamados.html', context)

@role_required('A', 'B', 'C')
def suport_chamado(request, chamado_id):
    context = get_user_profile(request)

    try:
        # Busca o chamado pelo ID
        chamado = models.ChChamado.objects.get(id=chamado_id, deletado=0)

        # Verifica se o usuário logado tem permissão para acessar o chamado
        user_role = context['user_role']
        chamado_role = chamado.id_usuario.id_grupo_usuario.nome  # Obtém o grupo do usuário que abriu o chamado

        # Define a hierarquia de permissões
        hierarquia = {
            'A': ['A', 'B', 'C'],  # A pode acessar todos
            'B': ['B', 'C'],       # B pode acessar B, C e Usuário Comum
            'C': ['C'],            # C pode acessar C e Usuário Comum
        }

        if chamado_role not in hierarquia.get(user_role, []):
            messages.error(request, 'Você não tem permissão para acessar este chamado.')
            return redirect('home')

        # Lida com o envio de mensagens
        if request.method == 'POST':
            mensagem = request.POST.get('mensagem')
            arquivo = request.FILES.get('arquivo')  # Obtém o arquivo enviado
            acao = request.POST.get('acao')  # Ação enviada pelo formulário (ex.: iniciar, responder, finalizar)

            if mensagem:
                usuario = models.UsuUsuario.objects.get(id=context['user_id'])

                # Atualiza o status do chamado com base na ação
                if acao == 'iniciar':
                    chamado.id_status = models.ChStatus.objects.get_or_create(nome='Chamado em Análise')[0]
                    chamado.id_usuario_suporte = usuario  # Define o técnico responsável
                    chamado.save()
                    messages.success(request, 'Atendimento iniciado com sucesso!')

                elif acao == 'responder_suporte':
                    chamado.id_status = models.ChStatus.objects.get_or_create(nome='Respondido pelo Suporte')[0]
                    chamado.save()
                    messages.success(request, 'Resposta enviada com sucesso!')

                elif acao == 'responder_usuario':
                    chamado.id_status = models.ChStatus.objects.get_or_create(nome='Respondido pelo Usuário')[0]
                    chamado.save()
                    messages.success(request, 'Resposta do usuário registrada com sucesso!')

                elif acao == 'finalizar':
                    chamado.id_status = models.ChStatus.objects.get_or_create(nome='Finalizado')[0]
                    chamado.save()
                    messages.success(request, 'Chamado finalizado com sucesso!')

                # Cria uma nova interação
                interacao = models.ChInteracao.objects.create(
                    id_usuario=usuario,
                    id_chamado=chamado,
                    id_status=chamado.id_status,
                    descricao=mensagem,
                    suporte=1 if user_role in ['A', 'B', 'C'] else 0,  # Define se é uma mensagem do suporte ou do usuário
                    data_cadastro=timezone.now()
                )

                # Se um arquivo foi enviado, cria um registro em ChArquivo
                if arquivo:
                    extensao = os.path.splitext(arquivo.name)[1].lower()[1:]
                    caminho_arquivo = default_storage.save(f'chamados/{chamado.id}/{arquivo.name}', arquivo)
                    models.ChArquivo.objects.create(
                        id_interacao=interacao,
                        arquivo=caminho_arquivo,
                        extensao=extensao,
                        tamanho=arquivo.size / (1024 * 1024),  # Tamanho em MB
                        deletado=0,
                        data_cadastro=timezone.now()
                    )

                return redirect('suport_chamado', chamado_id=chamado.id)
            else:
                messages.error(request, 'A mensagem não pode estar vazia.')

        # Busca as interações relacionadas ao chamado
        interacoes = models.ChInteracao.objects.filter(
            id_chamado=chamado
        ).select_related('id_usuario', 'id_status').order_by('data_cadastro')

        # Busca os arquivos relacionados às interações do chamado
        arquivos = models.ChArquivo.objects.filter(
            id_interacao__id_chamado=chamado,
        )

        # Atualiza o contexto com o chamado, interações e arquivos
        context.update({
            'chamado': chamado,
            'interacoes': interacoes,
            'arquivos': arquivos,
            'status_chamada': chamado.id_status,  # Status do chamado
            'categorias': chamado.chcategoriadochamado_set.all(),  # Categorias e subcategorias
            'solicitante': chamado.id_usuario,  # Usuário que abriu o chamado
            'patrimonio': chamado.patrimonio,  # Patrimônio associado ao chamado
            'data_cadastro': chamado.data_cadastro,  # Data de cadastro do chamado
            'tecnico_responsavel': chamado.id_usuario_suporte,  # Técnico responsável
            'cadastrado_por': chamado.id_usuario,  # Usuário que cadastrou o chamado
        })
    except models.ChChamado.DoesNotExist:
        messages.error(request, 'Chamado não encontrado.')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Erro ao carregar o chamado: {str(e)}')
        return redirect('home')

    return render(request, 'suport_chamado.html', context)