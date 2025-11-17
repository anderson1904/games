from django.contrib import admin
from django.urls import path, include
from Clash.views import *
from .models import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', PaginaLogin.as_view(), name='login'),
    path('logout/', PaginaLogout.as_view(), name='logout'),
    path('registro/', PaginaRegistro.as_view(), name='registro'),
    path('editar-perfil/', PaginaUserChange.as_view(), name='editar_perfil'),
    
    # URLs de CRUD de Notícias
    path('noticias/', NoticiaListView.as_view(), name='noticia_list'),
    path('noticias/nova/', NoticiaCreateView.as_view(), name='noticia_create'),
    path('noticias/<int:pk>/', NoticiaDetailView.as_view(), name='noticia_detail'),
    path('noticias/<int:pk>/editar/', NoticiaUpdateView.as_view(), name='noticia_update'),
    path('noticias/<int:pk>/deletar/', NoticiaDeleteView.as_view(), name='noticia_delete'),
]