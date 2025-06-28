from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('register_doctor/', views.register_doctor, name='register_doctor'),
    path('register_hospital/', views.register_hospital, name='register_hospital'),
    path('login/', views.login_view, name='login'),
    path('register_nurse/', views.register_nurse, name='register_nurse'),
    path('register_patient/', views.register_patient, name='register_patient'),
    path('create_case/', views.create_medical_case, name='create_case'),
    path('logout/', views.logout_view, name='logout'),
    path('patient_dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('nurse_dashboard/', views.nurse_dashboard, name='nurse_dashboard'),
    path('hospital_dashboard/', views.hospital_dashboard, name='hospital_dashboard'),
    path('nurse_queue/', views.nurse_queue, name='nurse_queue'),
    path('nurse/pick/<int:case_id>/', views.nurse_pick_case_view, name='pick_medical_case'),
    path('doctor_queue/', views.doctor_queue, name='doctor_queue'),
]
