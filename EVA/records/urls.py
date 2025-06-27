from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('register/hospital/', views.hospital_register, name='hospital_register'),
    path('register/doctor/', views.doctor_register, name='doctor_register'),
    path('register/nurse/', views.nurse_register, name='nurse_register'),
    path('register/patient/', views.patient_register, name='patient_register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
