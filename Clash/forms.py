# Clash/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import tbUser # Importe o seu modelo de usuário

class CustomUserCreationForm(UserCreationForm):
    # Adicione aqui os campos que você quer no formulário de registro,
    # além dos padrões (usuário, senha1, senha2).
    # O email é um bom campo para se ter no registro.
    email = forms.EmailField(required=True)
    Data_Nascimento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}) # Cria um seletor de data no HTML
    )

    class Meta(UserCreationForm.Meta):
        model = tbUser
        # Liste TODOS os campos que devem aparecer no formulário
        fields = UserCreationForm.Meta.fields + ('email', 'Data_Nascimento', 'Foto_Perfil',)