from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from .models import (
    tbUser, tbCartao, tbJogador, tbPartida, 
    tbStream, tbNoticia, tbProduto, tbFoto, 
    tbEspecifica, tbCompra
)

# _____________________________________________
# |                                           |
# |  Formulários de Usuários e Autenticação   |
# |___________________________________________|

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
        fields = UserCreationForm.Meta.fields + (
            'email',
            'Data_Nascimento',
            'Foto_Perfil',
        )

# Formulário baseado em ModelForm para o usuário editar o próprio perfil.
class CustomUserChangeForm(forms.ModelForm):
    # Define o modelo e os campos disponíveis.
    class Meta:
        model = tbUser

        # Campos do formulário que poderão ser alterados pelo usuário.
        fields = (
            'first_name',
            'last_name',
            'email',
            'Data_Nascimento',
            'Foto_Perfil',
        )

        # Define widgets personalizados para os campos.
        widgets = {
            'Data_Nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

class CartaoForm(forms.ModelForm):
    """
    Formulário para adicionar ou editar um cartão de crédito.
    """
    class Meta:
        model = tbCartao
        fields = (
            'Tipo_Cartao',
            'Numero_Cartao',
            'Nome_Cartao',
        )

class JogadorForm(forms.ModelForm):
    """
    Formulário para criar ou editar um Jogador.
    """
    class Meta:
        model = tbJogador
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
# |  Formulários de Conteúdo e Entretenimento |
# |___________________________________________|

class PartidaForm(forms.ModelForm):
    class Meta:
        model = tbPartida
        fields = ('Data_Prevista', 'Time_Adversario', 'Modalidade')
        widgets = {
            'Data_Prevista': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# FormSet para as Streams (Filhos)
StreamFormSet = inlineformset_factory(
    tbPartida,       # Modelo Pai
    tbStream,        # Modelo Filho
    fields=('tipo', 'embed'),
    extra=1,         # Quantos campos vazios aparecem (1 por padrão)
    can_delete=True  # Permite deletar streams existentes
)
class StreamForm(forms.ModelForm):
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
    class Meta:
        model = tbNoticia
        fields = ('Titulo', 'TextoHTML')
        # Removemos 'Partida' daqui, pois vamos criá-la manualmente

class PartidaOpcionalForm(forms.ModelForm):
    class Meta:
        model = tbPartida
        fields = ('Data_Prevista', 'Time_Adversario', 'Modalidade')
        widgets = {
            'Data_Prevista': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

class StreamOpcionalForm(forms.ModelForm):
    class Meta:
        model = tbStream
        fields = ('tipo', 'embed')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

# _____________________________________________
# |                                           |
# |       Formulários de Compras e Vendas     |
# |___________________________________________|

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = tbProduto
        fields = ('nome', 'tipo', 'preco_compra', 'preco_venda')

# --- FORMULÁRIO CUSTOMIZADO PARA FOTO + ESPECIFICAÇÃO ---

class FotoComSpecForm(forms.ModelForm):
    # Campo 1: Descrição (Ex: Azul)
    spec_descricao = forms.CharField(
        label="Nome da Opção (Ex: Azul, GG)",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Vazio se for foto comum', 'class': 'form-control'})
    )

    # Campo 2: Tipo (Ex: Cor) - NOVO!
    spec_tipo = forms.CharField(
        label="Tipo da Opção (Ex: Cor, Tamanho)",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Cor', 'class': 'form-control'})
    )

    class Meta:
        model = tbFoto
        fields = ('foto',)

# --- FORMSETS ---

# Formset Principal atualizado para usar o formulário híbrido
FotoProdutoFormSet = forms.inlineformset_factory(
    tbProduto,
    tbFoto,
    form=FotoComSpecForm,
    fields=('foto',),
    extra=1,
    can_delete=True 
)

