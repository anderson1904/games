# Clash/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import * 
# Importa todos os models (se eu já vou usar vários, pra que importar um por um?)

class CustomUserCreationForm(UserCreationForm): # formulário para criar um novo usuário
    
    email = forms.EmailField(required = True)# campo de email torna-se obrigatório
    Data_Nascimento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}) # Cria um seletor de data no HTML
        # widget é usado para customizar qual o tipo de campo no formulário
    )

    class Meta(UserCreationForm.Meta):
        model = tbUser
        # todos os campos que devem aparecer no formulário
        # é subclasse de UserCreationForm, já inclui dados de usuário padrão no django
        fields = UserCreationForm.Meta.fields + (
            'email',
            'Data_Nascimento',
            'Foto_Perfil',
        )# sendo necessário apenas acrecentar os campos extras do tbUser

class CustomUserChangeForm(forms.ModelForm):
    #Formulário para um usuário ATUALIZAR seu próprio perfil.
    class Meta:
        model = tbUser

        fields = (
            'first_name',
            'last_name',
            'email',
            'Data_Nascimento',
            'Foto_Perfil',
        )
        widgets = {
            'Data_Nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

class CartaoForm(forms.ModelForm):
    """
    Formulário para adicionar ou editar um cartão de crédito.
    (Nota: Seu modelo tbCartao precisa de um ForeignKey para tbUser!)
    """
    class Meta:
        model = tbCartao
        fields = (
            'Tipo_Cartao',
            'Numero_Cartao',
            'Nome_Cartao',
        )
        # Em um projeto real, você adicionaria widgets para formatar
        # a entrada do número do cartão e adicionar validação.


class JogadorForm(forms.ModelForm):
    """
    Formulário para criar ou editar um Jogador (provavelmente no admin).
    """
    class Meta:
        model = tbJogador
        # Note que não incluímos 'idade', pois é uma @property calculada.
        fields = (
            'Nome',
            'Nickname',
            'Data_Nascimento',
            'sobre',
            'trofeus',
            'Foto_Jogador',
        )
        widgets = {
            'Data_Nascimento': forms.DateInput(attrs={'type': 'date'}),
            'sobre': forms.Textarea(attrs={'rows': 4}),
        }

# _____________________________________________
# |                                           |
# |    Formulários de Conteúdo e Entretenimento   |
# |___________________________________________|

class PartidaForm(forms.ModelForm):
    """
    Formulário para agendar/editar uma Partida.
    (Nota: Seria melhor refatorar tbJogador_Partida para um ManyToManyField
    em tbPartida, o que simplificaria este formulário).
    """
    class Meta:
        model = tbPartida
        fields = (
            'Data_Prevista',
            'Time_Adversario',
            'Modalidade'
        )
        widgets = {
            'Data_Prevista': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

class StreamForm(forms.ModelForm):
    """
    Formulário para adicionar um link de stream a uma partida.
    Isso seria PERFEITO para usar como um inline_formset_factory
    na página de detalhes da Partida.
    """
    class Meta:
        model = tbStream
        fields = (
            'partida',
            'tipo',
            'embed',
            )
        widgets = {
            'embed': forms.Textarea(attrs={'rows': 3})
        }

class NoticiaForm(forms.ModelForm):
    """
    Formulário principal para criar ou editar uma Notícia.
    """
    class Meta:
        model = tbNoticia
        fields = (
            'Titulo',
            'TextoHTML',
            'Partida',
        )
        # O campo 'Partida' será um Dropdown.
        # 'TextoHTML' será um Textarea por padrão.
        # O modelo 'tbEdita' seria preenchido programaticamente na view,
        # associando o request.user ao salvar.


# _____________________________________________
# |                                           |
# |       Formulários de Compras e Vendas     |
# |___________________________________________|

class ProdutoForm(forms.ModelForm):
    """
    Formulário para um admin adicionar ou editar um Produto.
    """
    class Meta:
        model = tbProduto
        fields = (
            'nome',
            'tipo',
            'preco_compra',
            'preco_venda',
            'especificacoes',
        )
        # 'especificacoes' (M2M) aparecerá como uma caixa de seleção múltipla.
        # As 'tbFotos' seriam gerenciadas com um inline_formset_factory na view,
        # usando o formulário 'FotoForm' abaixo.

class FotoForm(forms.ModelForm):
    """
    Formulário para a 'tbFoto'. Quase nunca usado sozinho,
    mas sim com um inline_formset_factory na view de 'Produto'.
    """
    class Meta:
        model = tbFoto
        fields = ('foto')


class ItemCarrinhoUpdateForm(forms.ModelForm):
    """
    Este formulário NÃO é para criar um item (isso é feito com um botão).
    Este formulário é para ATUALIZAR a quantidade de um item
    que JÁ ESTÁ no carrinho.
    """
    class Meta:
        model = tbCompra # O modelo é 'tbCompra'
        fields = ('quantidade')
        widgets = {
            'quantidade': forms.NumberInput(attrs={'min': '1'})
        }