from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
from .models import *
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, CreateView, 
    UpdateView, DeleteView
)
from datetime import datetime as dt
from django.urls import reverse_lazy
from .forms import *
from .controls.carrinho import *
from django.contrib.auth.decorators import login_required


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

class NoticiaCreateView(LoginRequiredMixin, CreateView):
    model = tbNoticia
    form_class = NoticiaForm
    template_name = 'Clash/noticia_form.html'

    def get_context_data(self, **kwargs):
        """Envia os 3 formulários para o template"""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['partida_form'] = PartidaOpcionalForm(self.request.POST, prefix='partida')
            context['stream_form'] = StreamOpcionalForm(self.request.POST, prefix='stream')
        else:
            context['partida_form'] = PartidaOpcionalForm(prefix='partida')
            context['stream_form'] = StreamOpcionalForm(prefix='stream')
        return context

    def post(self, request, *args, **kwargs):
        """Processa o envio dos formulários"""
        # Instancia os forms com prefixos para não misturar os dados
        noticia_form = NoticiaForm(request.POST)
        partida_form = PartidaOpcionalForm(request.POST, prefix='partida')
        stream_form = StreamOpcionalForm(request.POST, prefix='stream')

        # Verifica se a notícia básica é válida
        if noticia_form.is_valid():
            
            # Verifica se o usuário tentou preencher dados da partida
            # (Checamos se 'Time_Adversario' foi preenchido)
            tem_partida = partida_form.data.get('partida-Time_Adversario')
            
            with transaction.atomic(): # Garante integridade do banco
                partida_criada = None
                
                if tem_partida:
                    # Se tem dados de partida, precisamos validar se estão completos
                    # Aqui forçamos a validação manual já que colocamos required=False no form
                    if all([partida_form.data.get('partida-Data_Prevista'), 
                            partida_form.data.get('partida-Time_Adversario'),
                            partida_form.data.get('partida-Modalidade')]):
                        
                        partida_criada = partida_form.save()
                        
                        # Se salvou a partida, tenta salvar o Stream
                        if stream_form.data.get('stream-tipo'):
                            stream = stream_form.save(commit=False)
                            stream.partida = partida_criada
                            stream.save()
                    else:
                        # Se preencheu partida pela metade, retorna erro
                        partida_form.add_error(None, "Preencha todos os campos da partida.")
                        return render(request, self.template_name, {
                            'form': noticia_form,
                            'partida_form': partida_form,
                            'stream_form': stream_form
                        })

                # Salva a Notícia
                noticia = noticia_form.save(commit=False)
                if partida_criada:
                    noticia.Partida = partida_criada
                noticia.save()

                # Cria o registro de Edição
                tbEdita.objects.create(
                    tbUser=self.request.user,
                    tbNoticia=noticia,
                    Data_Edicao=dt.now()
                )
                
                return redirect(reverse_lazy('noticia_detail', kwargs={'pk': noticia.pk}))
        
        # Se notícia for inválida, recarrega a página com erros
        return render(request, self.template_name, {
            'form': noticia_form,
            'partida_form': partida_form,
            'stream_form': stream_form
        })

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
        # Se for superusuário, pode editar qualquer uma
        if self.request.user.is_superuser:
            return queryset
        # Senão, só as que ele editou/criou
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



# --- LISTAR PRODUTOS ---
class ProdutoListView(LoginRequiredMixin, ListView):
    model = tbProduto
    template_name = 'Clash/produto_list.html'
    context_object_name = 'produtos'

# --- DETALHES DO PRODUTO ---
# Clash/views.py

class ProdutoDetailView(LoginRequiredMixin, DetailView):
    model = tbProduto
    template_name = 'Clash/produto_detail.html'
    context_object_name = 'produto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Vamos agrupar as especificações por TIPO
        # Estrutura final: {'Cor': [SpecAzul, SpecVermelha], 'Tamanho': [SpecG, SpecM]}
        specs_agrupadas = {}
        
        for spec in self.object.tbespecifica_set.all():
            nome_tipo = spec.tipo.nome if spec.tipo else "Outros"
            
            if nome_tipo not in specs_agrupadas:
                specs_agrupadas[nome_tipo] = []
            
            specs_agrupadas[nome_tipo].append(spec)
            
        context['specs_agrupadas'] = specs_agrupadas
        return context

# --- CRIAR PRODUTO (Complexo: Salva Produto + Fotos + Specs) ---
class ProdutoCreateView(LoginRequiredMixin, CreateView):
    model = tbProduto
    form_class = ProdutoForm
    template_name = 'Clash/produto_form.html'
    def get_success_url(self):
        # Redireciona para a página de detalhes do produto que acabou de ser criado
        return reverse_lazy('produto_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            # Só precisamos do formset de FOTOS agora
            data['fotos'] = FotoProdutoFormSet(self.request.POST, self.request.FILES)
        else:
            data['fotos'] = FotoProdutoFormSet()
        return data

def form_valid(self, form):
        context = self.get_context_data()
        fotos = context['fotos']
        
        with transaction.atomic():
            self.object = form.save()
            if fotos.is_valid():
                fotos.instance = self.object
                fotos.save()
                for formulario in fotos.forms:
                    if formulario.cleaned_data.get('DELETE') or not formulario.instance.pk:
                        continue
                    descricao_digitada = formulario.cleaned_data.get('spec_descricao')
                    tipo_digitado = formulario.cleaned_data.get('spec_tipo')
                    if descricao_digitada:
                        tipo_obj = None
                        if tipo_digitado:
                            tipo_obj, created = tbTipoEspecificacao.objects.get_or_create(
                                nome=tipo_digitado.strip().title()
                            )
                        tbEspecifica.objects.update_or_create(
                            produto=self.object,
                            foto=formulario.instance,
                            defaults={
                                'descricao': descricao_digitada,
                                'tipo': tipo_obj
                            }
                        )
                    else:
                        tbEspecifica.objects.filter(
                            produto=self.object, 
                            foto=formulario.instance
                        ).delete()
                
        return redirect(self.get_success_url())
# --- EDITAR PRODUTO ---
class ProdutoUpdateView(LoginRequiredMixin, UpdateView):
    model = tbProduto
    form_class = ProdutoForm
    template_name = 'Clash/produto_form.html' # Reutiliza o mesmo template
    
    def get_context_data(self, **kwargs):
        """
        Aqui nós PREPARAMOS os dados para mostrar na tela.
        O desafio é pegar o texto da tabela 'tbEspecifica' e colocar 
        dentro do campo 'spec_descricao' do formulário da foto.
        """
        data = super().get_context_data(**kwargs)
        
        if self.request.POST:
            # Se o usuário enviou dados, recarregamos o formset com o que ele mandou
            data['fotos'] = FotoProdutoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            # Se é apenas o carregamento da página:
            fotos_formset = FotoProdutoFormSet(instance=self.object)
            
            # --- LÓGICA DE PREENCHIMENTO AUTOMÁTICO ---
            # Iteramos sobre cada formulário de foto que já existe
            for form in fotos_formset.forms:
                if form.instance.pk: # Verifica se é uma foto salva (não é um form vazio extra)
                    # Tenta buscar se existe uma especificação para esta foto e este produto
                    spec = tbEspecifica.objects.filter(
                        produto=self.object, 
                        foto=form.instance
                    ).first()
                    
                    if spec:
                        # Se achou, preenche o campo 'spec_descricao' com o valor do banco
                        form.initial['spec_descricao'] = spec.descricao
            
            data['fotos'] = fotos_formset
            
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        fotos = context['fotos']
        
        with transaction.atomic():
            self.object = form.save()
            
            if fotos.is_valid():
                fotos.instance = self.object # Vincula ao produto
                fotos.save() # Salva as fotos e processa deleções
                
                for formulario in fotos.forms:
                    # Pula se for deletado ou vazio
                    if formulario.cleaned_data.get('DELETE') or not formulario.instance.pk:
                        continue
                    
                    # Pega os dados dos campos extras
                    descricao_digitada = formulario.cleaned_data.get('spec_descricao')
                    tipo_digitado = formulario.cleaned_data.get('spec_tipo')
                    
                    if descricao_digitada:
                        # 1. Resolve o TIPO (Busca ou Cria)
                        tipo_obj = None
                        if tipo_digitado:
                            # O .title() deixa a primeira letra maiúscula (Cor, Tamanho)
                            tipo_obj, created = tbTipoEspecificacao.objects.get_or_create(
                                nome=tipo_digitado.strip().title()
                            )
                        
                        # 2. Cria ou Atualiza a Especificação
                        tbEspecifica.objects.update_or_create(
                            produto=self.object,
                            foto=formulario.instance,
                            defaults={
                                'descricao': descricao_digitada,
                                'tipo': tipo_obj # Salva o tipo junto!
                            }
                        )
                    else:
                        # Se apagou a descrição, remove a especificação
                        tbEspecifica.objects.filter(
                            produto=self.object, 
                            foto=formulario.instance
                        ).delete()
                
                
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('produto_detail', kwargs={'pk': self.object.pk})


# --- DELETAR PRODUTO ---
class ProdutoDeleteView(LoginRequiredMixin, DeleteView):
    model = tbProduto
    template_name = 'Clash/produto_confirm_delete.html'
    success_url = reverse_lazy('produto_list')




class PartidaListView(ListView):
    model = tbPartida
    template_name = 'Clash/partida_list.html'
    context_object_name = 'partidas'
    ordering = ['-Data_Prevista'] # Ordena pela data, mais recentes/futuras primeiro

# --- DETALHES (Read) ---
class PartidaDetailView(DetailView):
    model = tbPartida
    template_name = 'Clash/partida_detail.html'
    context_object_name = 'partida'

# --- CRIAR (Create) ---
class PartidaCreateView(LoginRequiredMixin, CreateView):
    model = tbPartida
    form_class = PartidaForm
    template_name = 'Clash/partida_form.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['streams'] = StreamFormSet(self.request.POST)
        else:
            data['streams'] = StreamFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        streams = context['streams']
        
        with transaction.atomic():
            self.object = form.save() # Salva a partida
            
            if streams.is_valid():
                streams.instance = self.object # Liga as streams à partida criada
                streams.save()
                
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('partida_detail', kwargs={'pk': self.object.pk})

# --- EDITAR (Update) ---
class PartidaUpdateView(LoginRequiredMixin, UpdateView):
    model = tbPartida
    form_class = PartidaForm
    template_name = 'Clash/partida_form.html' # Reutiliza o template

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['streams'] = StreamFormSet(self.request.POST, instance=self.object)
        else:
            data['streams'] = StreamFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        streams = context['streams']
        
        with transaction.atomic():
            self.object = form.save() # Salva as alterações da partida
            
            if streams.is_valid():
                streams.save() # Salva/Deleta as streams
                
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('partida_detail', kwargs={'pk': self.object.pk})

# --- DELETAR (Delete) ---
class PartidaDeleteView(LoginRequiredMixin, DeleteView):
    model = tbPartida
    template_name = 'Clash/partida_confirm_delete.html'
    success_url = reverse_lazy('partida_list')