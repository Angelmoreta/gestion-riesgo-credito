from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q

from clientes.models import Cliente
from .models import AnalisisCredito, DocumentoAnalisis
from .forms import AnalisisCreditoForm, DocumentoAnalisisForm


class AnalisisCreditoListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los análisis de crédito"""
    model = AnalisisCredito
    template_name = 'creditos/analisis_list.html'
    context_object_name = 'analisis'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('cliente')
        # Filtro por búsqueda
        search = self.request.GET.get('q', '')
        if search:
            queryset = queryset.filter(
                Q(cliente__nombres__icontains=search) |
                Q(cliente__apellidos__icontains=search) |
                Q(cliente__numero_identificacion__icontains=search) |
                Q(estado__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Análisis de Crédito')
        context['search'] = self.request.GET.get('q', '')
        return context


class AnalisisCreditoDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver los detalles de un análisis de crédito"""
    model = AnalisisCredito
    template_name = 'creditos/analisis_detail.html'
    context_object_name = 'analisis'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Detalle del Análisis de Crédito')
        return context


class AnalisisCreditoCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo análisis de crédito"""
    model = AnalisisCredito
    form_class = AnalisisCreditoForm
    template_name = 'creditos/analisis_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        cliente_id = self.kwargs.get('cliente_id')
        if cliente_id:
            initial['cliente'] = get_object_or_404(Cliente, pk=cliente_id)
        return initial
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(
            self.request, 
            _('El análisis de crédito ha sido creado correctamente.')
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Nuevo Análisis de Crédito')
        context['form_action'] = _('Crear Análisis')
        return context


class AnalisisCreditoUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar un análisis de crédito existente"""
    model = AnalisisCredito
    form_class = AnalisisCreditoForm
    template_name = 'creditos/analisis_form.html'
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            _('El análisis de crédito ha sido actualizado correctamente.')
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Editar Análisis de Crédito')
        context['form_action'] = _('Actualizar Análisis')
        return context


class AnalisisCreditoDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar un análisis de crédito"""
    model = AnalisisCredito
    template_name = 'creditos/analisis_confirm_delete.html'
    success_url = reverse_lazy('creditos:analisis_lista')
    
    def delete(self, request, *args, **kwargs):
        messages.success(
            request, 
            _('El análisis de crédito ha sido eliminado correctamente.')
        )
        return super().delete(request, *args, **kwargs)


def calcular_puntaje(request):
    """Vista API para calcular el puntaje de crédito"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Aquí iría la lógica para calcular el puntaje de crédito
            # Por ahora, devolvemos un valor de ejemplo
            puntaje = 750
            return JsonResponse({
                'success': True,
                'puntaje': puntaje,
                'nivel_riesgo': 'Bajo' if puntaje > 700 else 'Medio' if puntaje > 600 else 'Alto'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

class DocumentoAnalisisCreateView(LoginRequiredMixin, CreateView):
    """Vista para subir documentos relacionados a un análisis de crédito"""
    model = DocumentoAnalisis
    form_class = DocumentoAnalisisForm
    template_name = 'creditos/documento_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        analisis_id = self.kwargs.get('analisis_id')
        if analisis_id:
            initial['analisis'] = get_object_or_404(AnalisisCredito, pk=analisis_id)
        return initial
    
    def form_valid(self, form):
        form.instance.subido_por = self.request.user
        messages.success(
            self.request,
            _('El documento ha sido subido correctamente.')
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('creditos:analisis_detalle', kwargs={'pk': self.object.analisis.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analisis_id = self.kwargs.get('analisis_id')
        context['analisis'] = get_object_or_404(AnalisisCredito, pk=analisis_id)
        context['title'] = _('Subir Documento')
        return context


class DocumentoAnalisisDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar un documento adjunto"""
    model = DocumentoAnalisis
    template_name = 'creditos/documento_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('creditos:analisis_detalle', 
                          kwargs={'pk': self.object.analisis.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(
            request,
            _('El documento ha sido eliminado correctamente.')
        )
        return super().delete(request, *args, **kwargs)


class AnalisisCreditoAprobarView(LoginRequiredMixin, UpdateView):
    """Vista para aprobar un análisis de crédito"""
    model = AnalisisCredito
    fields = []  # No necesitamos campos ya que solo actualizamos el estado
    template_name = 'creditos/analisis_aprobar.html'
    
    def form_valid(self, form):
        form.instance.estado = 'APR'
        form.instance.aprobado_por = self.request.user
        form.instance.fecha_aprobacion = timezone.now()
        messages.success(
            self.request,
            _('El análisis de crédito ha sido aprobado correctamente.')
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('creditos:analisis_detalle', kwargs={'pk': self.object.pk})


class AnalisisCreditoRechazarView(LoginRequiredMixin, UpdateView):
    """Vista para rechazar un análisis de crédito"""
    model = AnalisisCredito
    fields = ['motivo_rechazo']  # Solo necesitamos el campo de motivo
    template_name = 'creditos/analisis_rechazar.html'
    
    def form_valid(self, form):
        form.instance.estado = 'REC'
        form.instance.rechazado_por = self.request.user
        form.instance.fecha_rechazo = timezone.now()
        messages.success(
            self.request,
            _('El análisis de crédito ha sido rechazado correctamente.')
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('creditos:analisis_detalle', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Rechazar Análisis de Crédito')
        return context

# Create your views here.
