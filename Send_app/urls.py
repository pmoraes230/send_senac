from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

handler404 = 'Send_app.views.custom_404'

urlpatterns = [
    path("", views.login, name="login"),
    path("home/", views.home, name='home'),
    path("helpdesk/", views.helpdesk, name='helpdesk'),
    path('get_subcategories/', views.get_subcategories, name='get_subcategories'),
    path('logout/', views.logout_view, name='logout'),
    path('int_chamado/<int:chamado_id>/', views.int_chamado, name='int_chamado'),
    path('suport_chamado/<int:chamado_id>/', views.suport_chamado, name='suport_chamado'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)