from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from . import models

# Create your views here.
def login(request):
    username = request.POST.get('user')
    senha = request.POST.get('password')
    if request.method == 'GET':
        return render(request, 'login.html')
    user = get_object_or_404(models.UsuUsuario, login=username, senha=senha)
    if user:
        return redirect('home')
    else:
        return redirect('erro_login')
    
def erro_login(request):
    return render(request, 'login.html', {'error': 'Crendenciais inválida'})

def home(request):
    name_user = models.UsuUsuario.objects.all()
    return render(request, 'home.html', {'name_user': name_user})

def get_subcategories(request):
    category_id = request.GET.get('category_id')
    # Corrigido de categoria_id para id_categoria
    subcategories = models.ChSubcategoria.objects.filter(id_categoria=category_id).values('id', 'nome')
    return JsonResponse(list(subcategories), safe=False)

def helpdesk(request):
    name_user = models.UsuUsuario.objects.all()
    units = models.UsuUnidade.objects.all()
    sectors = models.UsuSetor.objects.all()
    categories = models.ChCategoria.objects.all()
    subcategories = models.ChSubcategoria.objects.all()

    return render(request, 'helpdesk.html', {
        'name_user': name_user,
        'units': units,
        'sectors': sectors,
        'categories': categories,
        'subcategories': subcategories,
    })