from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.urls import reverse

from clientes.models import Cliente


class AnalisisCredito(models.Model):
    """Modelo para el análisis de crédito de un cliente"""
    class EstadoAnalisis(models.TextChoices):
        PENDIENTE = 'PEN', _('Pendiente')
        APROBADO = 'APR', _('Aprobado')
        RECHAZADO = 'REC', _('Rechazado')
        EN_ESPERA = 'ESP', _('En espera')
        CANCELADO = 'CAN', _('Cancelado')
    
    class TipoCredito(models.TextChoices):
        PERSONAL = 'PER', _('Personal')
        HIPOTECARIO = 'HIP', _('Hipotecario')
        AUTOMOTRIZ = 'AUT', _('Automotriz')
        EDUCATIVO = 'EDU', _('Educativo')
        OTRO = 'OTR', _('Otro')
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='analisis_creditos',
        verbose_name=_('Cliente')
    )
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='analisis_realizados',
        verbose_name=_('Analista')
    )
    
    tipo_credito = models.CharField(
        _('Tipo de Crédito'),
        max_length=3,
        choices=TipoCredito.choices,
        default=TipoCredito.PERSONAL
    )
    
    monto_solicitado = models.DecimalField(
        _('Monto Solicitado'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    plazo_meses = models.PositiveIntegerField(
        _('Plazo en Meses'),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(360)  # 30 años como máximo
        ]
    )
    
    tasa_interes = models.DecimalField(
        _('Tasa de Interés Anual'),
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text=_('Tasa de interés anual en porcentaje (ej: 15.5)')
    )
    
    puntaje_credito = models.PositiveIntegerField(
        _('Puntaje de Crédito'),
        null=True,
        blank=True,
        validators=[MaxValueValidator(1000)]
    )
    
    estado = models.CharField(
        _('Estado'),
        max_length=3,
        choices=EstadoAnalisis.choices,
        default=EstadoAnalisis.PENDIENTE
    )
    
    ingresos_mensuales = models.DecimalField(
        _('Ingresos Mensuales'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    gastos_mensuales = models.DecimalField(
        _('Gastos Mensuales'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    deuda_actual = models.DecimalField(
        _('Deuda Actual'),
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    historial_crediticio = models.TextField(
        _('Historial Crediticio'),
        blank=True,
        help_text=_('Resumen del historial crediticio del cliente')
    )
    
    observaciones = models.TextField(
        _('Observaciones'),
        blank=True,
        help_text=_('Observaciones adicionales sobre el análisis')
    )
    
    fecha_analisis = models.DateTimeField(
        _('Fecha de Análisis'),
        auto_now_add=True
    )
    
    fecha_actualizacion = models.DateTimeField(
        _('Última Actualización'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('Análisis de Crédito')
        verbose_name_plural = _('Análisis de Créditos')
        ordering = ['-fecha_analisis']
        permissions = [
            ('can_approve_credit', 'Puede aprobar créditos'),
            ('can_reject_credit', 'Puede rechazar créditos'),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_credito_display()} - {self.cliente.get_nombre_completo()}"
    
    def get_absolute_url(self):
        return reverse('creditos:analisis_detalle', kwargs={'pk': self.pk})
    
    @property
    def capacidad_pago(self):
        """Calcula la capacidad de pago mensual"""
        if self.ingresos_mensuales <= 0:
            return 0
        return (self.ingresos_mensuales - self.gastos_mensuales) * 0.3  # 30% del ingreso disponible
    
    @property
    def cuota_mensual_estimada(self):
        """Calcula la cuota mensual estimada"""
        if self.plazo_meses == 0 or self.tasa_interes == 0:
            return 0
        
        # Fórmula para calcular la cuota de un préstamo: P * (r(1+r)^n) / ((1+r)^n - 1)
        # Donde P es el principal, r es la tasa de interés mensual, n es el número de pagos
        tasa_mensual = (self.tasa_interes / 100) / 12
        factor = (1 + tasa_mensual) ** self.plazo_meses
        cuota = self.monto_solicitado * (tasa_mensual * factor) / (factor - 1)
        return round(cuota, 2)
    
    @property
    def nivel_riesgo(self):
        """Determina el nivel de riesgo basado en el puntaje de crédito"""
        if self.puntaje_credito is None:
            return _('No evaluado')
        elif self.puntaje_credito >= 800:
            return _('Excelente')
        elif self.puntaje_credito >= 700:
            return _('Bueno')
        elif self.puntaje_credito >= 600:
            return _('Aceptable')
        else:
            return _('Riesgoso')
    
    def puede_aprobar(self):
        """Determina si el crédito puede ser aprobado basado en reglas de negocio"""
        if not self.puntaje_credito or self.puntaje_credito < 650:
            return False
        
        # Verificar que la cuota no exceda el 30% de los ingresos mensuales
        if self.cuota_mensual_estimada > self.capacidad_pago:
            return False
            
        # Verificar que la deuda total no exceda el 40% de los ingresos anuales
        deuda_total = self.deuda_actual + self.monto_solicitado
        if deuda_total > (self.ingresos_mensuales * 12 * 0.4):
            return False
            
        return True


class DocumentoAnalisis(models.Model):
    """Documentos adjuntos al análisis de crédito"""
    class TipoDocumento(models.TextChoices):
        IDENTIFICACION = 'IDE', _('Identificación')
        COMPROBANTE_INGRESOS = 'ING', _('Comprobante de Ingresos')
        REFERENCIA_BANCARIA = 'RB', _('Referencia Bancaria')
        REFERENCIA_COMERCIAL = 'RC', _('Referencia Comercial')
        OTRO = 'OTR', _('Otro')
    
    analisis = models.ForeignKey(
        AnalisisCredito,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name=_('Análisis de Crédito')
    )
    
    tipo_documento = models.CharField(
        _('Tipo de Documento'),
        max_length=3,
        choices=TipoDocumento.choices,
        default=TipoDocumento.OTRO
    )
    
    archivo = models.FileField(
        _('Archivo'),
        upload_to='creditos/documentos/%Y/%m/%d/'
    )
    
    fecha_subida = models.DateTimeField(
        _('Fecha de Subida'),
        auto_now_add=True
    )
    
    notas = models.TextField(
        _('Notas'),
        blank=True
    )
    
    class Meta:
        verbose_name = _('Documento de Análisis')
        verbose_name_plural = _('Documentos de Análisis')
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.get_tipo_documento_display()} - {self.analisis}"
    
    def get_absolute_url(self):
        return self.archivo.url if self.archivo else '#'

# Create your models here.
