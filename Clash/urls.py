from django.contrib import admin
from django.urls import path, include
from .models import *
from . import views

urlpatterns = [
    #admin
    path('admin/', admin.site.urls),
    path('pedidos/', views.PedidoListView.as_view(), name='lista_pedidos_admin'),

    # URLs de autenticação e perfil
    path('', views.home, name='home'),
    path('login/', views.PaginaLogin.as_view(), name='login'),
    path('logout/', views.PaginaLogout.as_view(), name='logout'),
    path('registro/', views.PaginaRegistro.as_view(), name='registro'),
    path('editar-perfil/', views.PaginaUserChange.as_view(), name='editar_perfil'),
    # URLs de CRUD de Notícias
    path('noticias/', views.NoticiaListView.as_view(), name='noticia_list'),
    path('noticias/nova/', views.NoticiaCreateView.as_view(), name='noticia_create'),
    path('noticias/<int:pk>/', views.NoticiaDetailView.as_view(), name='noticia_detail'),
    path('noticias/<int:pk>/editar/', views.NoticiaUpdateView.as_view(), name='noticia_update'),
    path('noticias/<int:pk>/deletar/', views.NoticiaDeleteView.as_view(), name='noticia_delete'),
    # URLs de CRUD de produtos
    path('produtos/', views.ProdutoListView.as_view(), name='produto_list'),
    path('produtos/novo/', views.ProdutoCreateView.as_view(), name='produto_create'),
    path('produtos/<int:pk>/', views.ProdutoDetailView.as_view(), name='produto_detail'),
    path('produtos/<int:pk>/editar/', views.ProdutoUpdateView.as_view(), name='produto_update'),
    path('produtos/<int:pk>/deletar/', views.ProdutoDeleteView.as_view(), name='produto_delete'),

    # URLs de CRUD DE PARTIDAS
    path('partidas/', views.PartidaListView.as_view(), name='partida_list'),
    path('partidas/nova/', views.PartidaCreateView.as_view(), name='partida_create'),
    path('partidas/<int:pk>/', views.PartidaDetailView.as_view(), name='partida_detail'),
    path('partidas/<int:pk>/editar/', views.PartidaUpdateView.as_view(), name='partida_update'),
    path('partidas/<int:pk>/deletar/', views.PartidaDeleteView.as_view(), name='partida_delete'),
    # URLs do carrinho de compras
    path('carrinho/adicionar/<int:pk>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/', views.CarrinhoView.as_view(), name='ver_carrinho'),
    path('carrinho/atualizar/<int:pk>/', views.atualizar_item_carrinho, name='atualizar_item'),
    path('carrinho/remover/<int:pk>/', views.remover_item_carrinho, name='remover_item'),
    path('carrinho/finalizar/', views.finalizar_compra, name='finalizar_compra'),
    
]