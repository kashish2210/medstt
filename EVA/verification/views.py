from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Profile
import random
from .helper import MessageHandler

def register(request):
    """OTP verification entry point: collect phone number and send OTP."""
    if request.method == "POST":
        # Generate OTP
        otp = random.randint(1000, 9999)
        
        # Create a temporary profile for OTP validation
        profile, _ = Profile.objects.get_or_create(phone_number=request.POST['phone_number'])
        profile.otp = f'{otp}'
        profile.save()

        # Send OTP via message or WhatsApp
        messagehandler = MessageHandler(request.POST['phone_number'], otp)
        if request.POST['methodOtp'] == "methodOtpWhatsapp":
            messagehandler.send_otp_via_whatsapp()
        else:
            messagehandler.send_otp_via_message()

        # Set a cookie for OTP validity and redirect to OTP verification
        red = redirect(f'/otp/{profile.uid}/')  # Redirect to OTP page
        red.set_cookie("can_otp_enter", "True", max_age=600)  # 10-minute validity
        return red

    return render(request, 'register1.html')


from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Profile

def otpVerify(request, uid):
    """Verify OTP for the user."""
    if request.method == "POST":
        try:
            profile = Profile.objects.get(uid=uid)
        except Profile.DoesNotExist:
            return HttpResponse("Profile does not exist.")

        # Check if the OTP can be entered (cookie exists)
        if request.COOKIES.get('can_otp_enter') is not None:
            if profile.otp == request.POST['otp']:
                return HttpResponse("Phone number verified successfully!")  # Replace with desired action
            return HttpResponse("Incorrect OTP.")
        
        return HttpResponse("10 minutes passed. Please try again.")
    
    return render(request, "otp.html", {'id': uid})
