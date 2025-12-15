from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from django.views.generic import DetailView

# Importe seus modelos corretamente (note os dois pontos .. para voltar pasta)
from ..models import tbProduto, tbCarrinho, tbCompra, tbPedido, tbItemPedido

@login_required
def adicionar_ao_carrinho(request, pk):
    produto = get_object_or_404(tbProduto, pk=pk)
    carrinho, created = tbCarrinho.objects.get_or_create(User=request.user)
    
    try:
        qtd_selecionada = int(request.POST.get('quantidade', 1))
        if qtd_selecionada < 1: qtd_selecionada = 1
    except ValueError:
        qtd_selecionada = 1

    specs_ids = []
    for key, value in request.POST.items():
        if key.startswith('spec_'):
            try:
                specs_ids.append(int(value))
            except (ValueError, TypeError):
                pass
    specs_ids.sort()

    itens_candidatos = tbCompra.objects.filter(carrinho=carrinho, produto=produto)
    item_existente = None
    
    for item in itens_candidatos:
        item_specs_ids = list(item.especificacoes.values_list('id', flat=True))
        item_specs_ids.sort()
        if item_specs_ids == specs_ids:
            item_existente = item
            break
    
    if item_existente:
        item_existente.quantidade += qtd_selecionada 
        item_existente.save()
        messages.success(request, f"+{qtd_selecionada} unidades de {produto.nome} adicionadas.")
    else:
        novo_item = tbCompra.objects.create(
            carrinho=carrinho,
            produto=produto,
            valor_compra=produto.preco_venda,
            quantidade=qtd_selecionada
        )
        if specs_ids:
            novo_item.especificacoes.set(specs_ids)
        messages.success(request, f"{qtd_selecionada}x {produto.nome} adicionado ao carrinho.")

    return redirect('ver_carrinho')

class CarrinhoView(LoginRequiredMixin, DetailView):
    model = tbCarrinho
    template_name = 'Clash/carrinho.html'
    context_object_name = 'carrinho'

    def get_object(self):
        carrinho, created = tbCarrinho.objects.get_or_create(User=self.request.user)
        return carrinho

@login_required
def atualizar_item_carrinho(request, pk):
    item = get_object_or_404(tbCompra, pk=pk)
    if request.method == 'POST':
        nova_quantidade = int(request.POST.get('quantidade', 1))
        if nova_quantidade > 0:
            item.quantidade = nova_quantidade
            item.save()
    return redirect('ver_carrinho')

@login_required
def remover_item_carrinho(request, pk):
    item = get_object_or_404(tbCompra, pk=pk)
    # Garante que só remove do próprio carrinho
    if item.carrinho.User == request.user:
        item.delete()
    return redirect('ver_carrinho')

@login_required
def finalizar_compra(request):
    carrinho = get_object_or_404(tbCarrinho, User=request.user)
    
    # Validação simples se tem itens
    if not carrinho.itens.exists():
        messages.warning(request, "Seu carrinho está vazio.")
        return redirect('produto_list') # ou 'ver_carrinho'

    # 1. Cria o Pedido no Histórico
    novo_pedido = tbPedido.objects.create(
        user=request.user,
        valor_total=carrinho.preco_total
    )

    # 2. Copia os itens do carrinho para os itens do pedido
    for item_carrinho in carrinho.itens.all():
        # Monta string das especificações para salvar no histórico
        lista_specs = []
        for spec in item_carrinho.especificacoes.all():
            tipo_nome = spec.tipo.nome if spec.tipo else "Opção"
            lista_specs.append(f"{tipo_nome}: {spec.descricao}")
        texto_specs = " | ".join(lista_specs)
        tbItemPedido.objects.create(
            pedido=novo_pedido,
            produto=item_carrinho.produto,
            nome_produto=item_carrinho.produto.nome,
            quantidade=item_carrinho.quantidade,
            preco_unitario=item_carrinho.valor_compra,
            especificacoes_texto=texto_specs
        )
    carrinho.itens.all().delete()
    messages.success(request, f"Pedido #{novo_pedido.id} realizado com sucesso!")

    return redirect('produto_list')

@login_required
def finalizar_compra(request):
    # 1. Pega o carrinho do usuário
    carrinho = get_object_or_404(tbCarrinho, User=request.user)
    
    # Se estiver vazio, não faz nada
    if not carrinho.itens.exists():
        messages.warning(request, "Seu carrinho está vazio.")
        return redirect('produto_list')

    # 2. Cria o Pedido (Cabeçalho)
    novo_pedido = tbPedido.objects.create(
        user=request.user,
        valor_total=carrinho.Preco_Total # Usa a property do model tbCarrinho
    )

    # 3. Copia cada item do carrinho para a tabela de histórico (tbItemPedido)
    for item_carrinho in carrinho.itens.all():
        
        # Formata as especificações em texto (ex: "Cor: Azul | Tamanho: G")
        lista_specs = []
        for spec in item_carrinho.especificacoes.all():
            tipo = spec.tipo.nome if spec.tipo else "Opção"
            lista_specs.append(f"{tipo}: {spec.descricao}")
        texto_specs = " | ".join(lista_specs)

        # Salva o item congelado
        tbItemPedido.objects.create(
            pedido=novo_pedido,
            produto=item_carrinho.produto,
            nome_produto=item_carrinho.produto.nome, # Salva o nome caso o produto seja deletado depois
            quantidade=item_carrinho.quantidade,
            preco_unitario=item_carrinho.valor_compra,
            especificacoes_texto=texto_specs
        )

    # 4. Limpa o carrinho
    carrinho.itens.all().delete()

    # 5. Mensagem de Sucesso e Redirecionamento
    messages.success(request, f"Sucesso! Seu pedido #{novo_pedido.id} foi realizado.")
    
    # Aqui você pode redirecionar para uma página de "Meus Pedidos" ou para a Loja
    return redirect('produto_list')

class PedidoListView(UserPassesTestMixin, ListView):
    model = tbPedido
    template_name = 'Clash/pedidos_admin.html'
    context_object_name = 'pedidos'
    ordering = ['-data_pedido'] 
    def test_func(self):
        return self.request.user.is_superuser

    # (Opcional) Se o usuário não for admin, redireciona para login ou home
    def handle_no_permission(self):
        from django.shortcuts import redirect
        return redirect('home')