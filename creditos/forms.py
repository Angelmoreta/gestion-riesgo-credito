from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from .models import AnalisisCredito, DocumentoAnalisis


class AnalisisCreditoForm(forms.ModelForm):
    """Formulario para el modelo AnalisisCredito"""
    class Meta:
        model = AnalisisCredito
        fields = [
            'tipo_credito', 'monto_solicitado', 'plazo_meses', 'tasa_interes',
            'ingresos_mensuales', 'gastos_mensuales', 'deuda_actual',
            'historial_crediticio', 'observaciones'
        ]
        widgets = {
            'historial_crediticio': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
            'tipo_credito': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'tasa_interes': _('Tasa de interés anual en porcentaje (ej: 15.5)'),
            'plazo_meses': _('Plazo en meses (máximo 360)'),
            'monto_solicitado': _('Monto total solicitado en la moneda local'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            if field_name != 'historial_crediticio' and field_name != 'observaciones':
                field.widget.attrs.update({'class': 'form-control'})
            if field.required:
                field.widget.attrs['required'] = 'required'
    
    def clean(self):
        cleaned_data = super().clean()
        ingresos = cleaned_data.get('ingresos_mensuales', 0)
        gastos = cleaned_data.get('gastos_mensuales', 0)
        
        # Validar que los gastos no superen los ingresos
        if ingresos and gastos and gastos > ingresos:
            self.add_error(
                'gastos_mensuales',
                _('Los gastos mensuales no pueden ser mayores a los ingresos mensuales.')
            )
        
        return cleaned_data


class DocumentoAnalisisForm(forms.ModelForm):
    """Formulario para el modelo DocumentoAnalisis"""
    class Meta:
        model = DocumentoAnalisis
        fields = ['tipo_documento', 'archivo', 'notas']
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 2}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            if field_name != 'notas':
                field.widget.attrs.update({'class': 'form-control'})
            if field.required:
                field.widget.attrs['required'] = 'required'
    
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo', False)
        if archivo:
            # Limitar el tamaño del archivo a 10MB
            max_size = 10 * 1024 * 1024  # 10MB
            if archivo.size > max_size:
                raise forms.ValidationError(
                    _('El archivo es muy grande. El tamaño máximo permitido es 10MB.')
                )
            
            # Validar la extensión del archivo
            ext = archivo.name.split('.')[-1].lower()
            valid_extensions = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    _('Formato de archivo no soportado. Formatos permitidos: PDF, DOC, DOCX, JPG, JPEG, PNG')
                )
                
        return archivo


class AnalisisCreditoAprobarForm(forms.Form):
    """Formulario para aprobar o rechazar un análisis de crédito"""
    ESTADO_CHOICES = (
        ('APR', _('Aprobar')),
        ('REC', _('Rechazar')),
        ('ESP', _('Marcar como en espera')),
    )
    
    estado = forms.ChoiceField(
        label=_('Acción'),
        choices=ESTADO_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True
    )
    
    comentario = forms.CharField(
        label=_('Comentario'),
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        help_text=_('Razón de la decisión (opcional)')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases de Bootstrap a los campos
        self.fields['estado'].widget.attrs.update({'class': 'form-check-input'})
