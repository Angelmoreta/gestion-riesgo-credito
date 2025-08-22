from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class Cliente(models.Model):
    """
    Modelo para almacenar información de los clientes
    """
    TIPO_IDENTIFICACION = [
        ('dni', 'DNI'),
        ('pasaporte', 'Pasaporte'),
        ('ruc', 'RUC'),
        ('ce', 'Carné de Extranjería'),
    ]
    
    ESTADO_CIVIL = [
        ('soltero', 'Soltero/a'),
        ('casado', 'Casado/a'),
        ('divorciado', 'Divorciado/a'),
        ('viudo', 'Viudo/a'),
        ('union_libre', 'Unión Libre'),
    ]
    
    # Información personal
    tipo_identificacion = models.CharField(
        _('Tipo de Identificación'), 
        max_length=20, 
        choices=TIPO_IDENTIFICACION,
        default='dni'
    )
    numero_identificacion = models.CharField(
        _('Número de Identificación'), 
        max_length=20, 
        unique=True
    )
    nombres = models.CharField(_('Nombres'), max_length=100)
    apellidos = models.CharField(_('Apellidos'), max_length=100)
    fecha_nacimiento = models.DateField(_('Fecha de Nacimiento'))
    lugar_nacimiento = models.CharField(_('Lugar de Nacimiento'), max_length=100)
    estado_civil = models.CharField(
        _('Estado Civil'), 
        max_length=20, 
        choices=ESTADO_CIVIL
    )
    
    # Información de contacto
    direccion = models.TextField(_('Dirección'))
    telefono = models.CharField(_('Teléfono'), max_length=20)
    celular = models.CharField(_('Celular'), max_length=20)
    email = models.EmailField(_('Correo Electrónico'), blank=True, null=True)
    
    # Información laboral
    ocupacion = models.CharField(_('Ocupación'), max_length=100)
    lugar_trabajo = models.CharField(_('Lugar de Trabajo'), max_length=200)
    ingreso_mensual = models.DecimalField(
        _('Ingreso Mensual'), 
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Información adicional
    fecha_registro = models.DateTimeField(_('Fecha de Registro'), auto_now_add=True)
    actualizado = models.DateTimeField(_('Última Actualización'), auto_now=True)
    notas = models.TextField(_('Notas Adicionales'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['apellidos', 'nombres']
    
    def __str__(self):
        return f"{self.apellidos}, {self.nombres} - {self.get_tipo_identificacion_display()}: {self.numero_identificacion}"
    
    def get_absolute_url(self):
        return reverse('clientes:detalle', kwargs={'pk': self.pk})
    
    def get_nombre_completo(self):
        """Devuelve el nombre completo del cliente"""
        return f"{self.nombres} {self.apellidos}"
    
    def get_edad(self):
        """Calcula la edad del cliente en años"""
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))


class ReferenciaPersonal(models.Model):
    """
    Modelo para almacenar referencias personales de los clientes
    """
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='referencias_personales',
        verbose_name=_('Cliente')
    )
    nombre_completo = models.CharField(_('Nombre Completo'), max_length=200)
    parentesco = models.CharField(_('Parentesco'), max_length=50)
    telefono = models.CharField(_('Teléfono'), max_length=20)
    direccion = models.TextField(_('Dirección'))
    
    class Meta:
        verbose_name = _('Referencia Personal')
        verbose_name_plural = _('Referencias Personales')
    
    def __str__(self):
        return f"{self.nombre_completo} ({self.parentesco}) - {self.telefono}"


class DocumentoCliente(models.Model):
    """
    Modelo para almacenar documentos relacionados con los clientes
    """
    TIPO_DOCUMENTO = [
        ('dni_frente', 'DNI (Frente)'),
        ('dni_dorso', 'DNI (Dorso)'),
        ('recibo_servicio', 'Recibo de Servicio'),
        ('recibo_sueldo', 'Recibo de Sueldo'),
        ('otro', 'Otro Documento'),
    ]
    
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='documentos',
        verbose_name=_('Cliente')
    )
    tipo_documento = models.CharField(
        _('Tipo de Documento'), 
        max_length=20, 
        choices=TIPO_DOCUMENTO
    )
    archivo = models.FileField(
        _('Archivo'), 
        upload_to='clientes/documentos/'
    )
    fecha_subida = models.DateTimeField(_('Fecha de Subida'), auto_now_add=True)
    notas = models.TextField(_('Notas'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Documento de Cliente')
        verbose_name_plural = _('Documentos de Clientes')
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.get_tipo_documento_display()} - {self.cliente}"
