from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from ..models import tbProduto, tbTipoEspecificacao, tbEspecifica
from ..forms import ProdutoForm, FotoProdutoFormSet

class ProdutoListView(LoginRequiredMixin, ListView):
    model = tbProduto
    template_name = 'Clash/produto_list.html'
    context_object_name = 'produtos'

class ProdutoDetailView(LoginRequiredMixin, DetailView):
    model = tbProduto
    template_name = 'Clash/produto_detail.html'
    context_object_name = 'produto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        specs_agrupadas = {}
        for spec in self.object.tbespecifica_set.all():
            nome_tipo = spec.tipo.nome if spec.tipo else "Outros"
            if nome_tipo not in specs_agrupadas:
                specs_agrupadas[nome_tipo] = []
            specs_agrupadas[nome_tipo].append(spec)
        context['specs_agrupadas'] = specs_agrupadas
        return context

class ProdutoCreateView(LoginRequiredMixin, CreateView):
    model = tbProduto
    form_class = ProdutoForm
    template_name = 'Clash/produto_form.html'
    
    def get_success_url(self):
        return reverse_lazy('produto_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
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

class ProdutoUpdateView(LoginRequiredMixin, UpdateView):
    model = tbProduto
    form_class = ProdutoForm
    template_name = 'Clash/produto_form.html'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['fotos'] = FotoProdutoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            fotos_formset = FotoProdutoFormSet(instance=self.object)
            for form in fotos_formset.forms:
                if form.instance.pk:
                    spec = tbEspecifica.objects.filter(
                        produto=self.object, 
                        foto=form.instance
                    ).first()
                    if spec:
                        form.initial['spec_descricao'] = spec.descricao
                        if spec.tipo:
                            form.initial['spec_tipo'] = spec.tipo.nome
            data['fotos'] = fotos_formset
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        fotos = context['fotos']
        
        with transaction.atomic():
            self.object = form.save()
            if fotos.is_valid():
                fotos.save()
                for formulario in fotos.forms:
                    if formulario.cleaned_data.get('DELETE'):
                        continue
                    
                    if formulario.instance.pk:
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
                                defaults={'descricao': descricao_digitada, 'tipo': tipo_obj}
                            )
                        else:
                            tbEspecifica.objects.filter(
                                produto=self.object, 
                                foto=formulario.instance
                            ).delete()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('produto_detail', kwargs={'pk': self.object.pk})

class ProdutoDeleteView(LoginRequiredMixin, DeleteView):
    model = tbProduto
    template_name = 'Clash/produto_confirm_delete.html'
    success_url = reverse_lazy('produto_list')