from django.shortcuts import render
from django.http import JsonResponse
from . import models

# Create your views here.

def index(request):
    total_cliques = models.cliques.objects.count()

    if request.method == 'POST':
        models.cliques.objects.create()
    
    return render(request, 'index.html', {'total_cliques': total_cliques})