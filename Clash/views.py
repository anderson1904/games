from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView, 
    DeleteView
)
from datetime import datetime as dt
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomUserChangeForm, NoticiaForm

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

def home(request):
    return render(request, 'Clash/base.html')

class NoticiaCreateView(LoginRequiredMixin, CreateView):
    model = tbNoticia
    form_class = NoticiaForm
    template_name = 'Clash/noticia_form.html' # Reutiliza o template de formulário

    def form_valid(self, form):
        # Salva a notícia e nos dá o objeto (self.object)
        response = super().form_valid(form) 
        
        # Cria o registro de autoria na tabela tbEdita
        tbEdita.objects.create(
            tbUser=self.request.user,
            tbNoticia=self.object,
            Data_Edicao=dt.now(),    
        )
        return response

    def get_success_url(self):
        return reverse_lazy('noticia_detail', kwargs={'pk': self.object.pk})

# --- READ (Listar) ---
class NoticiaListView(ListView):
    model = tbNoticia
    template_name = 'Clash/noticia_list.html'
    context_object_name = 'noticias'
    ordering = ['-id']

# --- READ (Detalhe) ---
class NoticiaDetailView(DetailView):
    model = tbNoticia
    template_name = 'Clash/noticia_detail.html'
    context_object_name = 'noticia'

# --- UPDATE (Atualizar/Editar) ---
class NoticiaUpdateView(LoginRequiredMixin, UpdateView):
    model = tbNoticia
    form_class = NoticiaForm
    template_name = 'Clash/noticia_form.html'
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(tbedita__tbUser=self.request.user)

    def form_valid(self, form):
        noticia = form.save()
        tbEdita.objects.create(
            tbUser=self.request.user,
            tbNoticia=noticia
        )
        return redirect(self.get_success_url())
    def get_success_url(self):
        return reverse_lazy('noticia_detail', kwargs={'pk': self.object.pk})

# --- DELETE (Deletar) ---
class NoticiaDeleteView(LoginRequiredMixin, DeleteView):
    model = tbNoticia
    template_name = 'Clash/noticia_confirm_delete.html'
    success_url = reverse_lazy('noticia_list')
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(tbedita__tbUser = self.request.user)