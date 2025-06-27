# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.esp32, name='esp32'),
    path('start/', views.start_recording, name='start_recording'),
    path('stop/', views.stop_recording, name='stop_recording'),
]
