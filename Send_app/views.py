from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.utils import timezone
import os
from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from . import models

# Create your views here.
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
    username = request.POST.get('user')
    senha = request.POST.get('password')
    if request.method == 'GET':
        return render(request, 'login.html')
    try:
        user = models.UsuUsuario.objects.get(login=username, senha=senha)
    except models.UsuUsuario.DoesNotExist:
        return redirect('erro_login')
    # Configure a sessão com as informações do usuário
    request.session['user_id'] = user.id
    request.session['user_name'] = user.nome_exibicao or user.nome
    return redirect('home')
    
def erro_login(request):
    username = request.POST.get('user')
    senha = request.POST.get('password')
    if request.method == 'GET':
        return render(request, 'login.html')
    try:
        user = models.UsuUsuario.objects.get(login=username, senha=senha)
    except models.UsuUsuario.DoesNotExist:
        return render(request, 'login.html', {'error': 'Crendenciais inválida'})
    # Configure a sessão com as informações do usuário
    request.session['user_id'] = user.id
    request.session['user_name'] = user.nome_exibicao or user.nome

    return redirect('home')

def logout_view(request):
    logout(request)
    return redirect('login')  # Redireciona para a página de login

def home(request):
    context = get_user_profile(request)
    if not context.get('is_authenticated'):
        return redirect('login')
    # Busca o status "Aberto"
    status_aberto = models.ChStatus.objects.get(nome='Aberto')
    # Usa o nome padrão do relacionamento reverso
    chamados_abertos = models.ChChamado.objects.filter(
        id_status=status_aberto,
        deletado=0
    ).select_related(
        'id_usuario', 'id_setor', 'id_usuario_suporte', 'id_setor_suporte'
    ).prefetch_related(
        'chcategoriadochamado_set__id_categoria', 
        'chcategoriadochamado_set__id_subcategoria'
    )
    context.update({
        'chamados_abertos': chamados_abertos,
    })
    
    return render(request, 'home.html', context)

def get_subcategories(request):
    category_id = request.GET.get('category_id')
    # Corrigido de categoria_id para id_categoria
    subcategories = models.ChSubcategoria.objects.filter(id_categoria=category_id).values('id', 'nome')
    return JsonResponse(list(subcategories), safe=False)

def helpdesk(request):
    context = get_user_profile(request)
    
    if not context.get('is_authenticated'):
        return redirect('login')
    
    if request.method == 'POST':
        try:
            usuario_id = request.POST.get('id_usuario')
            setor_id = request.POST.get('id_setor')
            patrimonio = request.POST.get('patrimonio')
            descricao = request.POST.get('description')
            arquivos = request.FILES.getlist('arquivo')
            categorias = [value for key, value in request.POST.items() if key.startswith('id_categoria_')]
            subcategorias = [value for key, value in request.POST.items() if key.startswith('id_subcategoria_')]
            
            # Obter ou criar o status "Aberto"
            status, created = models.ChStatus.objects.get_or_create(nome='Aberto')
            if created:
                messages.info(request, 'Status "Aberto" foi criado automaticamente.')
            
            # Obter objetos
            usuario = models.UsuUsuario.objects.get(id=int(usuario_id), ativo=1, deletado=0)
            setor = models.UsuSetor.objects.get(id=int(setor_id))
            unidade = usuario.id_unidade
            
            # Criar chamado usando o usuário como id_usuario_suporte temporário
            chamado = models.ChChamado.objects.create(
                id_usuario=usuario,
                id_setor=setor,
                id_unidade=unidade,
                id_usuario_suporte=usuario,  # Usa o usuário que abriu o chamado como suporte temporário
                id_setor_suporte=setor,      # Usa o setor do chamado como setor de suporte temporário
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
            for cat_id, subcat_id in zip(categorias, subcategorias):
                categoria = models.ChCategoria.objects.get(id=int(cat_id))
                subcategoria = models.ChSubcategoria.objects.get(id=int(subcat_id))
                models.ChCategoriaDoChamado.objects.create(
                    id_chamado=chamado,
                    id_subcategoria=subcategoria,
                    id_categoria=categoria
                )
            
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
        
        except (models.UsuUsuario.DoesNotExist, models.UsuSetor.DoesNotExist, models.ChCategoria.DoesNotExist, models.ChSubcategoria.DoesNotExist):
            messages.error(request, 'Um ou mais valores selecionados são inválidos.')
        except Exception as e:
            messages.error(request, f'Erro ao abrir chamado: {str(e)}')
        
        return redirect('helpdesk')
    
    context.update({
        'name_user': models.UsuUsuario.objects.all(),
        'units': models.UsuUnidade.objects.all(),
        'sectors': models.UsuSetor.objects.all(),
        'categories': models.ChCategoria.objects.all(),
        'subcategories': models.ChSubcategoria.objects.all(),
    })
    
    return render(request, 'helpdesk.html', context)