from django.urls import path
from . import views

urlpatterns = [
    path('verify/', views.register, name='verify'),  # URL for initiating OTP verification
    path('otp/<str:uid>/', views.otpVerify, name='otp'),  # URL for verifying the OTP
]
