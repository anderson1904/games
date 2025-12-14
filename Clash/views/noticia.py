from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from datetime import datetime as dt

from ..models import tbNoticia, tbEdita, tbPartida, tbStream
from ..forms import NoticiaForm, PartidaOpcionalForm, StreamOpcionalForm

class NoticiaCreateView(LoginRequiredMixin, CreateView):
    model = tbNoticia
    form_class = NoticiaForm
    template_name = 'Clash/noticia_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['partida_form'] = PartidaOpcionalForm(self.request.POST, prefix='partida')
            context['stream_form'] = StreamOpcionalForm(self.request.POST, prefix='stream')
        else:
            context['partida_form'] = PartidaOpcionalForm(prefix='partida')
            context['stream_form'] = StreamOpcionalForm(prefix='stream')
        return context

    def post(self, request, *args, **kwargs):
        noticia_form = NoticiaForm(request.POST)
        partida_form = PartidaOpcionalForm(request.POST, prefix='partida')
        stream_form = StreamOpcionalForm(request.POST, prefix='stream')

        if noticia_form.is_valid():
            tem_partida = partida_form.data.get('partida-Time_Adversario')
            
            with transaction.atomic():
                partida_criada = None
                
                if tem_partida:
                    if all([partida_form.data.get('partida-Data_Prevista'), 
                            partida_form.data.get('partida-Time_Adversario'),
                            partida_form.data.get('partida-Modalidade')]):
                        
                        partida_criada = partida_form.save()
                        
                        if stream_form.data.get('stream-tipo'):
                            stream = stream_form.save(commit=False)
                            stream.partida = partida_criada
                            stream.save()
                    else:
                        partida_form.add_error(None, "Preencha todos os campos da partida.")
                        return render(request, self.template_name, {
                            'form': noticia_form,
                            'partida_form': partida_form,
                            'stream_form': stream_form
                        })

                noticia = noticia_form.save(commit=False)
                if partida_criada:
                    noticia.Partida = partida_criada
                noticia.save()

                tbEdita.objects.create(
                    tbUser=self.request.user,
                    tbNoticia=noticia,
                    Data_Edicao=dt.now()
                )
                
                return redirect(reverse_lazy('noticia_detail', kwargs={'pk': noticia.pk}))
        
        return render(request, self.template_name, {
            'form': noticia_form,
            'partida_form': partida_form,
            'stream_form': stream_form
        })

class NoticiaListView(ListView):
    model = tbNoticia
    template_name = 'Clash/noticia_list.html'
    context_object_name = 'noticias'
    ordering = ['-id']

class NoticiaDetailView(DetailView):
    model = tbNoticia
    template_name = 'Clash/noticia_detail.html'
    context_object_name = 'noticia'

class NoticiaUpdateView(LoginRequiredMixin, UpdateView):
    model = tbNoticia
    form_class = NoticiaForm
    template_name = 'Clash/noticia_form.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(tbedita__tbUser=self.request.user)

    def form_valid(self, form):
        noticia = form.save()
        tbEdita.objects.create(
            tbUser=self.request.user,
            tbNoticia=noticia,
            Data_Edicao=dt.now()
        )
        return redirect(self.get_success_url())
        
    def get_success_url(self):
        return reverse_lazy('noticia_detail', kwargs={'pk': self.object.pk})

class NoticiaDeleteView(LoginRequiredMixin, DeleteView):
    model = tbNoticia
    template_name = 'Clash/noticia_confirm_delete.html'
    success_url = reverse_lazy('noticia_list')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(tbedita__tbUser=self.request.user)