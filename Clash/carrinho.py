from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import tbProduto, tbCarrinho, tbCompra, tbEspecifica
@login_required
def add_to_cart(request, pk):
    produto = get_object_or_404(tbProduto, pk=pk)
    carrinho, created = tbCarrinho.objects.get_or_create(User=request.user)
    specs_ids = request.POST.getlist('especificacao') 
    
    # 2. Lógica difícil: Encontrar se já existe item igual no carrinho
    # Buscamos todos os itens deste produto neste carrinho
    itens_candidatos = tbCompra.objects.filter(carrinho=carrinho, produto=produto)
    item_existente = None
    
    # Convertemos os IDs que vieram do form para inteiros e ordenamos para comparar
    specs_ids = []
    for key, value in request.POST.items():
        if key.startswith('spec_'): # Pega spec_Cor, spec_Tamanho, etc.
            specs_ids.append(value)

    for item in itens_candidatos:
        # Pega os IDs das specs desse item no banco
        item_specs_ids = list(item.especificacoes.values_list('id', flat=True))
        item_specs_ids.sort()
        
        # Se as listas forem idênticas, achamos o item!
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
            novo_item.especificacoes.set(specs_ids)
        
        messages.success(request, f"{produto.nome} adicionado ao carrinho.")

    return redirect('ver_carrinho')