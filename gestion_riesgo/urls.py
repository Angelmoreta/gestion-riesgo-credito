"""
URL configuration for gestion_riesgo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

# Import views
from . import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Curso protegido
    path('curso/', views.curso, name='curso'),
    
    # Home
    path('', views.home, name='home'),
    
    # Apps
    path('clientes/', include('clientes.urls', namespace='clientes')),
    path('creditos/', include('creditos.urls', namespace='creditos')),
    path('libro/', include('libro.urls', namespace='libro')),  # Actualizado para usar la app libro
    
    # API
    path('api/consent/', views.log_consent, name='api_consent'),
    
    # Legal
    path('legal/aviso-legal/', TemplateView.as_view(template_name='legal/aviso_legal.html'), name='aviso_legal'),
    path('legal/politica-privacidad/', TemplateView.as_view(template_name='legal/politica_privacidad.html'), name='politica_privacidad'),
    path('legal/politica-cookies/', TemplateView.as_view(template_name='legal/politica_cookies.html'), name='politica_cookies'),
    
    # Test pages - wrapped in login_required using the method_decorator
    path('test-responsive/', 
         login_required(TemplateView.as_view(template_name='test_responsive.html')), 
         name='test_responsive'),
    path('test-interactive/', 
         login_required(TemplateView.as_view(template_name='test_interactive.html')), 
         name='test_interactive'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
