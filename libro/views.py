from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def libro_portada(request):
    return render(request, 'libro/portada.html')

@login_required
def libro_intro(request):
    return render(request, 'libro/intro_riesgo_credito.html')
