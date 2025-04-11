from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.login, name="login"),
    path("home/", views.home, name='home'),
    path("helpdesk/", views.helpdesk, name='helpdesk'),
    path("erro_login/", views.erro_login, name='erro_login'),
    path('get_subcategories/', views.get_subcategories, name='get_subcategories'),
    path('logout/', views.logout_view, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
