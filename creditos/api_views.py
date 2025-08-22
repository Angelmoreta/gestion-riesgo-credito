from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

from clientes.models import Cliente
from .models import AnalisisCredito
import json

@login_required
@require_http_methods(["GET"])
def buscar_clientes(request):
    """
    API view para buscar clientes por nombre, apellido o número de identificación.
    Devuelve resultados en formato JSON para ser usados en autocompletado o búsquedas dinámicas.
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 3:
        return JsonResponse({
            'success': False,
            'error': _('Ingrese al menos 3 caracteres para buscar')
        }, status=400)
    
    try:
        # Buscar clientes que coincidan con la consulta
        clientes = Cliente.objects.filter(
            Q(nombres__icontains=query) |
            Q(apellidos__icontains=query) |
            Q(numero_identificacion__icontains=query)
        )[:10]  # Limitar a 10 resultados
        
        # Serializar los resultados
        resultados = []
        for cliente in clientes:
            resultados.append({
                'id': cliente.id,
                'nombres': cliente.nombres,
                'apellidos': cliente.apellidos,
                'tipo_identificacion': cliente.tipo_identificacion,
                'tipo_identificacion_display': cliente.get_tipo_identificacion_display(),
                'numero_identificacion': cliente.numero_identificacion,
                'telefono': cliente.telefono or '',
                'email': cliente.email or '',
                'ingreso_mensual': float(cliente.ingreso_mensual) if cliente.ingreso_mensual else None,
                'url': f'/clientes/{cliente.id}/',
            })
        
        return JsonResponse({
            'success': True,
            'count': len(resultados),
            'results': resultados
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt  # Solo para desarrollo, en producción usar CSRF token
def calcular_puntaje_credito(request):
    """
    API view para calcular el puntaje de crédito basado en los datos proporcionados.
    Se espera un JSON con los datos del formulario.
    """
    try:
        # Obtener datos del cuerpo de la petición
        data = json.loads(request.body)
        
        # Aquí iría la lógica real para calcular el puntaje de crédito
        # Por ahora, devolvemos un valor simulado basado en los datos de entrada
        
        # Simular cálculo de puntaje (300-850)
        puntaje_base = 650  # Puntaje base
        
        # Ajustes basados en ingresos vs gastos
        ingresos = float(data.get('ingresos_mensuales', 0))
        gastos = float(data.get('gastos_mensuales', 0))
        deuda_actual = float(data.get('deuda_actual', 0))
        monto_solicitado = float(data.get('monto_solicitado', 0))
        
        if ingresos > 0:
            # Ajuste por relación deuda/ingresos
            deuda_total = deuda_actual + monto_solicitado
            ratio_deuda_ingresos = deuda_total / (ingresos * 12)  # Deuda total vs ingreso anual
            
            if ratio_deuda_ingresos < 0.3:
                puntaje_base += 50
            elif ratio_deuda_ingresos > 0.8:
                puntaje_base -= 100
                
            # Ajuste por capacidad de ahorro
            capacidad_ahorro = (ingresos - gastos) / ingresos if ingresos > 0 else 0
            if capacidad_ahorro > 0.3:
                puntaje_base += 50
            elif capacidad_ahorro < 0.1:
                puntaje_base -= 50
        
        # Ajuste por monto solicitado
        if monto_solicitado > 0:
            if monto_solicitado > ingresos * 12:  # Si el monto es mayor al ingreso anual
                puntaje_base -= 100
            
        # Asegurar que el puntaje esté dentro del rango 300-850
        puntaje = max(300, min(850, puntaje_base))
        
        # Determinar nivel de riesgo
        if puntaje >= 800:
            nivel_riesgo = 'Excelente'
            clase_riesgo = 'success'
        elif puntaje >= 700:
            nivel_riesgo = 'Bueno'
            clase_riesgo = 'success'
        elif puntaje >= 600:
            nivel_riesgo = 'Aceptable'
            clase_riesgo = 'warning'
        else:
            nivel_riesgo = 'Riesgoso'
            clase_riesgo = 'danger'
        
        # Calcular cuota mensual estimada
        plazo_meses = int(data.get('plazo_meses', 12))
        tasa_interes = float(data.get('tasa_interes', 0)) / 100 / 12  # Tasa mensual
        
        if plazo_meses > 0 and tasa_interes > 0 and monto_solicitado > 0:
            factor = (1 + tasa_interes) ** plazo_meses
            cuota_mensual = (monto_solicitado * tasa_interes * factor) / (factor - 1)
        else:
            cuota_mensual = 0
        
        # Calcular capacidad de pago (30% del ingreso disponible)
        capacidad_pago = (ingresos - gastos) * 0.3 if ingresos > gastos else 0
        
        return JsonResponse({
            'success': True,
            'puntaje': puntaje,
            'nivel_riesgo': nivel_riesgo,
            'clase_riesgo': clase_riesgo,
            'cuota_mensual': round(cuota_mensual, 2),
            'capacidad_pago': round(capacidad_pago, 2),
            'recomendacion_aprobacion': puntaje >= 650 and cuota_mensual <= capacidad_pago
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': _('Formato de datos inválido')
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def obtener_datos_cliente(request, cliente_id):
    """
    API view para obtener los datos de un cliente específico por su ID.
    """
    try:
        cliente = Cliente.objects.get(pk=cliente_id)
        
        # Obtener el último análisis de crédito del cliente (si existe)
        ultimo_analisis = AnalisisCredito.objects.filter(
            cliente=cliente
        ).order_by('-fecha_analisis').first()
        
        # Datos del cliente
        datos_cliente = {
            'id': cliente.id,
            'nombre_completo': cliente.get_nombre_completo(),
            'tipo_identificacion': cliente.get_tipo_identificacion_display(),
            'numero_identificacion': cliente.numero_identificacion,
            'telefono': cliente.telefono or '',
            'email': cliente.email or '',
            'ingreso_mensual': float(cliente.ingreso_mensual) if cliente.ingreso_mensual else None,
            'direccion': cliente.direccion or '',
            'fecha_registro': cliente.fecha_registro.strftime('%d/%m/%Y') if cliente.fecha_registro else None,
        }
        
        # Datos del último análisis (si existe)
        datos_analisis = None
        if ultimo_analisis:
            datos_analisis = {
                'fecha': ultimo_analisis.fecha_analisis.strftime('%d/%m/%Y'),
                'tipo_credito': ultimo_analisis.get_tipo_credito_display(),
                'monto_solicitado': float(ultimo_analisis.monto_solicitado) if ultimo_analisis.monto_solicitado else None,
                'plazo_meses': ultimo_analisis.plazo_meses,
                'tasa_interes': float(ultimo_analisis.tasa_interes) if ultimo_analisis.tasa_interes else None,
                'estado': ultimo_analisis.get_estado_display(),
                'puntaje_credito': ultimo_analisis.puntaje_credito,
                'url': ultimo_analisis.get_absolute_url(),
            }
        
        return JsonResponse({
            'success': True,
            'cliente': datos_cliente,
            'ultimo_analisis': datos_analisis
        })
        
    except Cliente.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': _('Cliente no encontrado')
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
