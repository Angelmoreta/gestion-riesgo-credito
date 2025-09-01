from django.urls import path
from . import views

app_name = 'libro'
urlpatterns = [
    path('', views.libro_portada, name='portada'),
    path('introduccion/', views.libro_intro, name='intro'),
]
