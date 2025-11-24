from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import tbProduto, tbCarrinho, tbCompra, tbEspecifica
# Clash/views.py

@login_required
def add_to_cart(request, pk):
    produto = get_object_or_404(tbProduto, pk=pk)
    carrinho, created = tbCarrinho.objects.get_or_create(User=request.user)
    
    # --- CORREÇÃO AQUI ---
    # 1. Coleta os IDs, converte para INTEIRO e ordena
    specs_ids = []
    for key, value in request.POST.items():
        if key.startswith('spec_'):
            try:
                specs_ids.append(int(value)) # Converte '1' para 1
            except (ValueError, TypeError):
                pass # Ignora se não for número
    
    specs_ids.sort() # Ordena: [1, 5] (Cor Azul, Tamanho G)
    # ---------------------

    # 2. Busca itens candidatos (mesmo produto no carrinho)
    itens_candidatos = tbCompra.objects.filter(carrinho=carrinho, produto=produto)
    item_existente = None
    
    for item in itens_candidatos:
        # Pega os IDs das specs desse item no banco
        # values_list já retorna inteiros se o campo for ID
        item_specs_ids = list(item.especificacoes.values_list('id', flat=True))
        item_specs_ids.sort() # Ordena para garantir a comparação: [1, 5]
        
        # Agora compara: [1, 5] == [1, 5] -> True!
        if item_specs_ids == specs_ids:
            item_existente = item
            break
    
    if item_existente:
        item_existente.quantidade += 1
        item_existente.save()
        messages.success(request, f"+1 unidade de {produto.nome} adicionada.")
    else:
        # Cria um novo item
        novo_item = tbCompra.objects.create(
            carrinho=carrinho,
            produto=produto,
            valor_compra=produto.preco_venda,
            quantidade=1
        )
        # Adiciona as relações ManyToMany
        if specs_ids:
            novo_item.especificacoes.set(specs_ids) # O .set() aceita lista de IDs
        
        messages.success(request, f"{produto.nome} adicionado ao carrinho.")

    return redirect('ver_carrinho')


@login_required
def atualizar_item_carrinho(request, pk):
    """Atualiza a quantidade de um item específico"""
    item = get_object_or_404(tbCompra, pk=pk)
    if request.method == 'POST':
        nova_quantidade = int(request.POST.get('quantidade', 1))
        if nova_quantidade > 0:
            item.quantidade = nova_quantidade
            item.save()
    return redirect('ver_carrinho')

@login_required
def remover_item_carrinho(request, pk):
    """Remove um item do carrinho"""
    item = get_object_or_404(tbCompra, pk=pk)
    # Garante que o usuário só delete o SEU próprio item (segurança)
    if item.carrinho.User == request.user:
        item.delete()
    
    return redirect('ver_carrinho')

