from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Cliente, ReferenciaPersonal, DocumentoCliente
from .forms import ClienteForm, ReferenciaPersonalForm, DocumentoClienteForm


class ClienteListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los clientes"""
    model = Cliente
    template_name = 'clientes/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtro por búsqueda
        search = self.request.GET.get('q', '')
        if search:
            queryset = queryset.filter(
                models.Q(nombres__icontains=search) |
                models.Q(apellidos__icontains=search) |
                models.Q(numero_identificacion__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Lista de Clientes')
        context['search'] = self.request.GET.get('q', '')
        return context


class ClienteDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver los detalles de un cliente"""
    model = Cliente
    template_name = 'clientes/cliente_detail.html'
    context_object_name = 'cliente'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Detalle del Cliente')
        return context


class ClienteCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo cliente"""
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            _('El cliente ha sido creado correctamente.')
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Nuevo Cliente')
        context['form_action'] = _('Crear Cliente')
        return context


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar un cliente existente"""
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            _('Los datos del cliente han sido actualizados correctamente.')
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Editar Cliente')
        context['form_action'] = _('Actualizar Cliente'
        )
        return context


class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar un cliente"""
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:lista')
    
    def delete(self, request, *args, **kwargs):
        messages.success(
            request, 
            _('El cliente ha sido eliminado correctamente.')
        )
        return super().delete(request, *args, **kwargs)


# Vistas para Referencias Personales
class ReferenciaPersonalCreateView(LoginRequiredMixin, CreateView):
    """Vista para agregar una referencia personal a un cliente"""
    model = ReferenciaPersonal
    form_class = ReferenciaPersonalForm
    template_name = 'clientes/referencia_form.html'
    
    def form_valid(self, form):
        form.instance.cliente_id = self.kwargs['cliente_id']
        messages.success(
            self.request, 
            _('La referencia personal ha sido agregada correctamente.')
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('clientes:detalle', kwargs={'pk': self.kwargs['cliente_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Agregar Referencia Personal')
        context['cliente'] = get_object_or_404(Cliente, pk=self.kwargs['cliente_id'])
        return context


class ReferenciaPersonalUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar una referencia personal"""
    model = ReferenciaPersonal
    form_class = ReferenciaPersonalForm
    template_name = 'clientes/referencia_form.html'
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            _('La referencia personal ha sido actualizada correctamente.')
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('clientes:detalle', kwargs={'pk': self.object.cliente_id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Editar Referencia Personal')
        context['cliente'] = self.object.cliente
        return context


class ReferenciaPersonalDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar una referencia personal"""
    model = ReferenciaPersonal
    template_name = 'clientes/referencia_confirm_delete.html'
    
    def get_success_url(self):
        messages.success(
            self.request, 
            _('La referencia personal ha sido eliminada correctamente.')
        )
        return reverse('clientes:detalle', kwargs={'pk': self.object.cliente_id})


# Vistas para Documentos del Cliente
class DocumentoClienteCreateView(LoginRequiredMixin, CreateView):
    """Vista para subir un documento para un cliente"""
    model = DocumentoCliente
    form_class = DocumentoClienteForm
    template_name = 'clientes/documento_form.html'
    
    def form_valid(self, form):
        form.instance.cliente_id = self.kwargs['cliente_id']
        messages.success(
            self.request, 
            _('El documento ha sido subido correctamente.')
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('clientes:detalle', kwargs={'pk': self.kwargs['cliente_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Subir Documento')
        context['cliente'] = get_object_or_404(Cliente, pk=self.kwargs['cliente_id'])
        return context


class DocumentoClienteDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar un documento de un cliente"""
    model = DocumentoCliente
    template_name = 'clientes/documento_confirm_delete.html'
    
    def get_success_url(self):
        messages.success(
            self.request, 
            _('El documento ha sido eliminado correctamente.')
        )
        return reverse('clientes:detalle', kwargs={'pk': self.object.cliente_id})
