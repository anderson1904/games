from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import tbUser
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm

class PaginaLogin(LoginView):
    """
    CBV para a página de login.
    """
    # Define o template que será usado para renderizar o formulário de login.
    template_name = 'Clash/login.html' # Vamos criar este arquivo no próximo passo
    
    # Se o usuário já estiver logado, redireciona ele para a página inicial.
    #redirect_authenticated_user = True

    # Define para onde o usuário será redirecionado após um login bem-sucedido.
    # Usamos reverse_lazy para evitar erros de importação circular.
    # OBS: É ainda melhor definir isso no settings.py (veja Passo 4).
    def get_success_url(self):
        return reverse_lazy('home') # 'index' é o nome da URL da sua página inicial

class PaginaLogout(LogoutView):
    """
    CBV para fazer o logout do usuário.
    Não precisa de um template, pois apenas desloga e redireciona.
    """
    # Define para onde o usuário será redirecionado após o logout.
    # OBS: É ainda melhor definir isso no settings.py (veja Passo 4).
    def get_next_page(self):
        return redirect('home') # Redireciona para a página de login após sair

class PaginaRegistro(CreateView):
    """
    CBV para a página de registro de novos usuários.
    """
    # Define o formulário que será usado pela view.
    form_class = CustomUserCreationForm
    
    # Define o template que será renderizado.
    template_name = 'Clash/registro.html' # Vamos criar este arquivo a seguir
    
    # Define para onde o usuário será redirecionado após um registro bem-sucedido.
    # reverse_lazy('login') é perfeito: após se registrar, o usuário vai para a página de login.
    success_url = reverse_lazy('login')

def home(request):
    
    return render(request, 'Clash/base.html')

