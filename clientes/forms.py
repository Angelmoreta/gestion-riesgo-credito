from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Cliente, ReferenciaPersonal, DocumentoCliente


class ClienteForm(forms.ModelForm):
    """Formulario para el modelo Cliente"""
    class Meta:
        model = Cliente
        fields = [
            'tipo_identificacion', 'numero_identificacion',
            'nombres', 'apellidos', 'fecha_nacimiento', 'lugar_nacimiento',
            'estado_civil', 'direccion', 'telefono', 'celular', 'email',
            'ocupacion', 'lugar_trabajo', 'ingreso_mensual', 'notas'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            if field_name != 'notas':
                field.widget.attrs.update({'class': 'form-control'})
            if field.required:
                field.widget.attrs['required'] = 'required'


class ReferenciaPersonalForm(forms.ModelForm):
    """Formulario para el modelo ReferenciaPersonal"""
    class Meta:
        model = ReferenciaPersonal
        fields = ['nombre_completo', 'parentesco', 'telefono', 'direccion']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            if field.required:
                field.widget.attrs['required'] = 'required'


class DocumentoClienteForm(forms.ModelForm):
    """Formulario para el modelo DocumentoCliente"""
    class Meta:
        model = DocumentoCliente
        fields = ['tipo_documento', 'archivo', 'notas']
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            if field.required:
                field.widget.attrs['required'] = 'required'
    
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo', False)
        if archivo:
            # Limitar el tamaño del archivo a 5MB
            max_size = 5 * 1024 * 1024  # 5MB
            if archivo.size > max_size:
                raise forms.ValidationError(
                    _('El archivo es muy grande. El tamaño máximo permitido es 5MB.')
                )
        return archivo
