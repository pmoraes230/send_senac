from django.urls import path
from .views import helpdesk, login, home

urlpatterns = [
    path("", login, name="login"),
    path("home/", home, name='home'),
    path("helpdesk/", helpdesk, name='helpdesk')
]
