
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    tbUser, tbCartao, tbJogador, tbPartida, tbJogador_Partida,
    tbStream, tbNoticia, tbEdita, tbCarrinho, tbProduto, tbFoto,
    tbEspecifica, tbCompra
)

# --- CONFIGURAÇÃO PARA O SEU USUÁRIO CUSTOMIZADO ---
# Precisamos estender o UserAdmin padrão para incluir seus campos extras
class CustomUserAdmin(UserAdmin):
    # Adiciona seus campos extras ao painel de edição do usuário
    fieldsets = UserAdmin.fieldsets + (
        ('Campos Personalizados', {'fields': ('Data_Nascimento', 'Foto_Perfil')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Campos Personalizados', {'fields': ('Data_Nascimento', 'Foto_Perfil')}),
    )

# --- INLINES PARA EDITAR MODELOS RELACIONADOS NA MESMA PÁGINA ---

class StreamInline(admin.TabularInline):
    model = tbStream
    extra = 1 # Mostra 1 campo extra para adicionar nova stream

class ItemCompraInline(admin.TabularInline):
    model = tbCompra
    extra = 0 # Não mostra campos extras, apenas os itens existentes
    readonly_fields = ('valor_total',) # Mostra o valor total, mas não deixa editar

class FotoInline(admin.TabularInline):
    model = tbFoto
    extra = 1

# --- CLASSES DE ADMIN PRINCIPAIS ---

@admin.register(tbJogador)
class JogadorAdmin(admin.ModelAdmin):
    list_display = ('Nickname', 'Nome', 'trofeus')
    search_fields = ('Nickname', 'Nome')
    list_filter = ('trofeus',)

@admin.register(tbPartida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('Time_Adversario', 'Data_Prevista', 'Modalidade')
    search_fields = ('Time_Adversario', 'Modalidade')
    list_filter = ('Modalidade', 'Data_Prevista')
    inlines = [StreamInline] # Permite adicionar/editar streams na página da partida

@admin.register(tbNoticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('Titulo', 'Partida')
    search_fields = ('Titulo',)
    list_filter = ('Partida',)

@admin.register(tbCarrinho)
class CarrinhoAdmin(admin.ModelAdmin):
    list_display = ('User',) # O ideal seria mostrar o username do usuário
    inlines = [ItemCompraInline] # Mostra os itens do carrinho na mesma página

@admin.register(tbProduto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'preco_venda')
    search_fields = ('nome', 'tipo')
    list_filter = ('tipo',)
    inlines = [FotoInline] # Mostra e permite adicionar fotos na página do produto

# --- REGISTRO DOS MODELOS RESTANTES ---
# Para os modelos que não precisam de muita customização, podemos registrar de forma simples.

# Registra nosso Custom User
admin.site.register(tbUser, CustomUserAdmin)

# Registra os outros modelos
admin.site.register(tbCartao)
admin.site.register(tbJogador_Partida) # Tabela de ligação
admin.site.register(tbEdita) # Tabela de ligação
admin.site.register(tbEspecifica) # Tabela de ligação
admin.site.register(tbCompra) # Já aparece no carrinho, mas bom ter separado também