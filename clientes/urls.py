from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # Lista de clientes
    path('', views.ClienteListView.as_view(), name='lista'),
    
    # Detalle de cliente
    path('<int:pk>/', views.ClienteDetailView.as_view(), name='detalle'),
    
    # Crear cliente
    path('nuevo/', views.ClienteCreateView.as_view(), name='crear'),
    
    # Editar cliente
    path('<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='editar'),
    
    # Eliminar cliente
    path('<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='eliminar'),
]
