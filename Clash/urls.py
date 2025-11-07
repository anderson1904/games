from django.contrib import admin
from django.urls import path, include
from Clash.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', PaginaLogin.as_view(), name='login'),
    path('logout/', PaginaLogout.as_view(), name='logout'),
    path('registro/', PaginaRegistro.as_view(), name='registro'),
    path('editar-perfil/', PaginaUserChange.as_view(), name='editar_perfil'),

]