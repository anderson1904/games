from django.urls import reverse_lazy
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from ..models import tbPartida
from ..forms import PartidaForm, StreamFormSet # Supondo que StreamFormSet está no forms.py

class PartidaListView(ListView):
    model = tbPartida
    template_name = 'Clash/partida_list.html'
    context_object_name = 'partidas'
    ordering = ['-Data_Prevista']

class PartidaDetailView(DetailView):
    model = tbPartida
    template_name = 'Clash/partida_detail.html'
    context_object_name = 'partida'

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
            self.object = form.save()
            if streams.is_valid():
                streams.instance = self.object
                streams.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('partida_detail', kwargs={'pk': self.object.pk})

class PartidaUpdateView(LoginRequiredMixin, UpdateView):
    model = tbPartida
    form_class = PartidaForm
    template_name = 'Clash/partida_form.html'

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
            self.object = form.save()
            if streams.is_valid():
                streams.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('partida_detail', kwargs={'pk': self.object.pk})

class PartidaDeleteView(LoginRequiredMixin, DeleteView):
    model = tbPartida
    template_name = 'Clash/partida_confirm_delete.html'
    success_url = reverse_lazy('partida_list')