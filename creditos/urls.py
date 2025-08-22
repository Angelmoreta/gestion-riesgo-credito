from django.urls import path
from . import views
from . import api_views

app_name = 'creditos'

urlpatterns = [
    # Lista de análisis de crédito
    path('', views.AnalisisCreditoListView.as_view(), name='analisis_lista'),
    
    # Detalle de análisis de crédito
    path('<int:pk>/', views.AnalisisCreditoDetailView.as_view(), name='analisis_detalle'),
    
    # Crear nuevo análisis
    path('nuevo/', views.AnalisisCreditoCreateView.as_view(), name='analisis_nuevo'),
    
    # Editar análisis existente
    path('<int:pk>/editar/', views.AnalisisCreditoUpdateView.as_view(), name='analisis_editar'),
    
    # Eliminar análisis
    path('<int:pk>/eliminar/', views.AnalisisCreditoDeleteView.as_view(), name='analisis_eliminar'),
    
    # Subir documento
    path('<int:analisis_id>/documento/nuevo/', views.DocumentoAnalisisCreateView.as_view(), name='documento_nuevo'),
    
    # Eliminar documento
    path('documento/<int:pk>/eliminar/', views.DocumentoAnalisisDeleteView.as_view(), name='documento_eliminar'),
    
    # Acciones sobre el análisis
    path('<int:pk>/aprobar/', views.AnalisisCreditoAprobarView.as_view(), name='analisis_aprobar'),
    path('<int:pk>/rechazar/', views.AnalisisCreditoRechazarView.as_view(), name='analisis_rechazar'),
    
    # API Endpoints
    path('api/calcular-puntaje/', api_views.calcular_puntaje_credito, name='api_calcular_puntaje'),
    
    # API v2 - Mejorada y con más funcionalidades
    path('api/v2/clientes/buscar/', api_views.buscar_clientes, name='api_buscar_clientes'),
    path('api/v2/calcular-puntaje/', api_views.calcular_puntaje_credito, name='api_v2_calcular_puntaje'),
    path('api/v2/clientes/<int:cliente_id>/', api_views.obtener_datos_cliente, name='api_obtener_cliente'),
]
