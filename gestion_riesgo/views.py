from django.shortcuts import render

# Create your views here.
def home(request):
    """
    Vista para la página de inicio
    """
    context = {
        'title': 'Inicio',
    }
    return render(request, 'home.html', context)
