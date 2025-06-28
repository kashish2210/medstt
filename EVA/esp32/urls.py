# urls.py (add these to your ESP32 app urls or main urls.py)

from django.urls import path
from . import views

urlpatterns = [
    path('', views.esp32, name='esp32'),
    path('start/', views.start_recording, name='start_recording'),
    path('stop/', views.stop_recording, name='stop_recording'),
    path('get-transcription/', views.get_transcription, name='get_transcription'),
    path('download-pdf/', views.download_pdf_report, name='download_pdf_report'),
    path('view-report/', views.view_json_report, name='view_json_report'),
]
