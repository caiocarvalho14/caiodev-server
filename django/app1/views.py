from django.shortcuts import render
from django.http import JsonResponse
from . import models
from .startup import SERVER_STARTED_AT
from datetime import datetime, timezone

# Create your views here.

def index(request):
    total_cliques = models.cliques.objects.count()
    uptime = datetime.now(timezone.utc) - SERVER_STARTED_AT

    if request.method == 'POST':
        models.cliques.objects.create()
    
    return render(request, 'index.html', {'total_cliques': total_cliques, "started_at": SERVER_STARTED_AT.__format__("%H:%M:%S"), "uptime_seconds": int(uptime.total_seconds())})

def uptime(request):
    uptime = datetime.now(timezone.utc) - SERVER_STARTED_AT
    return JsonResponse({'uptime': int(uptime.total_seconds())})