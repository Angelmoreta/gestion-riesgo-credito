from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json

# Create your views here.
def home(request):
    """
    Vista para la página de inicio
    """
    context = {
        'title': 'Inicio',
    }
    return render(request, 'home.html', context)

@login_required
def curso(request):
    context = {
        'title': 'Curso de Riesgo de Crédito',
    }
    return render(request, 'curso.html', context)

@login_required
def libro_riesgo_credito(request):
    context = {
        'title': 'Libro: ¿Qué es el riesgo de crédito?'
    }
    return render(request, 'libro/intro_riesgo_credito.html', context)

@login_required
def libro_portada(request):
    context = {
        'title': 'Libro: Riesgo de Crédito',
    }
    return render(request, 'libro/portada.html', context)

@csrf_exempt
def log_consent(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    action = payload.get('action')  # 'accept' | 'reject' | 'update'
    analytics = bool(payload.get('analytics', False))
    # Caducidad por defecto: 12 meses
    expires_at = timezone.now() + timezone.timedelta(days=365)

    # Obtener IP real si está detrás de proxy
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')
    ua = request.META.get('HTTP_USER_AGENT', '')

    # Usuario si está autenticado (opcional)
    user = request.user if request.user.is_authenticated else None

    try:
        from creditos.models import ConsentLog
        ConsentLog.objects.create(
            action=action or 'update',
            analytics=analytics,
            expires_at=expires_at,
            ip=ip,
            user_agent=ua,
            user=user,
        )
    except Exception as e:
        # Evitar romper UX si hay un problema guardando
        return JsonResponse({'status': 'ok', 'logged': False})

    return JsonResponse({'status': 'ok', 'logged': True})
