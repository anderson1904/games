from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from ..models import tbJogador, tbProduto, tbNoticia, tbUser
from ..forms import CustomUserCreationForm, CustomUserChangeForm

def home(request):
    lista_jogadores = tbJogador.objects.all()
    lista_produtos = tbProduto.objects.all()
    lista_noticias = tbNoticia.objects.all().order_by('-id')[:3]
    
    contexto = {
        'jogadores': lista_jogadores,
        'produtos': lista_produtos,
        'noticias': lista_noticias,
    }
    return render(request, 'Clash/base.html', contexto)

class PaginaLogin(LoginView):
    template_name = 'Clash/login.html'
    def get_success_url(self):
        return reverse_lazy('home')

class PaginaLogout(LogoutView):
    def get_next_page(self):
        return redirect('home')

class PaginaRegistro(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'Clash/registro.html' 
    success_url = reverse_lazy('login')

class PaginaUserChange(LoginRequiredMixin, UpdateView):
    model = tbUser
    form_class = CustomUserChangeForm
    template_name = 'Clash/edit_user.html'
    success_url = reverse_lazy('home')
    def get_object(self, queryset=None):
        return self.request.user