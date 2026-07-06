from django.contrib import admin
from django.urls import include, path, include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('uptime', views.uptime, name='uptime')
]
