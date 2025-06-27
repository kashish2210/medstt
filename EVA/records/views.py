from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Hospital, Doctor, Nurse, Patient
from .forms import (
    HospitalRegistrationForm, 
    DoctorRegistrationForm, 
    NurseRegistrationForm, 
    PatientRegistrationForm
)

def register_view(request):
    """Main registration page with user type selection"""
    return render(request, 'register.html')
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

    return render(request, 'register.html')

def hospital_register(request):
    """Hospital registration view"""
    if request.method == 'POST':
        form = HospitalRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Create the custom user
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    user_type='hospital',
                    phone=form.cleaned_data['phone']
                )

                # Create hospital object (QR handled in model's save method)
                hospital = Hospital.objects.create(
                    user=user,
                    name=form.cleaned_data['name'],
                    address=form.cleaned_data['address']
                )

                messages.success(request, 'Hospital registered successfully! Please login.')
                return redirect('login')

            except Exception as e:
                messages.error(request, f"Error during registration: {str(e)}")

    else:
        form = HospitalRegistrationForm()

    return render(request, 'hospital.html', {'form': form})
def hospital_register(request):
    """Hospital registration view"""
    if request.method == 'POST':
        form = HospitalRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Create the custom user
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    user_type='hospital',
                    phone=form.cleaned_data['phone']
                )

                # Create hospital object (QR handled in model's save method)
                hospital = Hospital.objects.create(
                    user=user,
                    name=form.cleaned_data['name'],
                    address=form.cleaned_data['address']
                )

                messages.success(request, 'Hospital registered successfully! Please login.')
                return redirect('login')

            except Exception as e:
                messages.error(request, f"Error during registration: {str(e)}")

    else:
        form = HospitalRegistrationForm()

    return render(request, 'hospital.html', {'form': form})

def doctor_register(request):
    """Doctor registration view"""
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                user_type='doctor',
                phone=form.cleaned_data['phone'],
                age=form.cleaned_data['age']
            )
            
            # Create doctor profile
            Doctor.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                age=form.cleaned_data['age'],
                phone=form.cleaned_data['phone'],
                speciality=form.cleaned_data['speciality'],
                gender=form.cleaned_data['gender'],
                room_clinic_number=form.cleaned_data['room_clinic_number'],
                hospital_code=form.cleaned_data['hospital_code']
            )
            
            messages.success(request, 'Doctor registered successfully! Please login.')
            return redirect('login')
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'doctor.html', {'form': form})

def nurse_register(request):
    """Nurse registration view"""
    if request.method == 'POST':
        form = NurseRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                user_type='nurse',
                phone=form.cleaned_data['phone'],
                age=form.cleaned_data['age']
            )
            
            # Create nurse profile
            Nurse.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                age=form.cleaned_data['age'],
                gender=form.cleaned_data['gender'],
                hospital_code=form.cleaned_data['hospital_code']
            )
            
            messages.success(request, 'Nurse registered successfully! Please login.')
            return redirect('login')
    else:
        form = NurseRegistrationForm()
    
    return render(request, 'nurse.html', {'form': form})

def patient_register(request):
    """Patient registration view"""
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                user_type='patient',
                phone=form.cleaned_data['phone'],
                age=form.cleaned_data['age']
            )
            
            # Create patient profile
            Patient.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                age=form.cleaned_data['age'],
                phone=form.cleaned_data['phone'],
                gender=form.cleaned_data['gender'],
                problem_diseases=form.cleaned_data['problem_diseases'],
                medicines_consumed=form.cleaned_data['medicines_consumed'],
                medicine_countdown=form.cleaned_data['medicine_countdown'],
                visibility=form.cleaned_data['visibility']
            )
            
            messages.success(request, 'Patient registered successfully! Please login.')
            return redirect('login')
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'patient.html', {'form': form})

def login_view(request):
    """Login view for all user types"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    """Dashboard view after login"""
    user = request.user
    context = {'user': user}
    
    if user.user_type == 'hospital':
        hospital = user.hospital_profile
        context['hospital'] = hospital
        context['doctors'] = hospital.doctors.all()
        context['nurses'] = hospital.nurses.all()
        context['rooms'] = hospital.rooms.all()
    elif user.user_type == 'doctor':
        doctor = user.doctor_profile
        context['doctor'] = doctor
        context['queues'] = doctor.queues.filter(is_completed=False)
        context['cases'] = doctor.cases.all()
    elif user.user_type == 'nurse':
        nurse = user.nurse_profile
        context['nurse'] = nurse
    elif user.user_type == 'patient':
        patient = user.patient_profile
        context['patient'] = patient
        context['cases'] = patient.medical_cases.all()
        context['queues'] = patient.queue_set.filter(is_completed=False)
    
    return render(request, 'dashboard.html', context)
def save(self, *args, **kwargs):
    # Generate hospital code only if not already set
    if not self.hospital_code:
        self.hospital_code = str(uuid.uuid4())[:8].upper()

    creating = self._state.adding  # Check if creating for the first time
    super().save(*args, **kwargs)  # First save to get 'id'

    # Generate QR after first save
    if creating and not self.registration_qr:
        qr_data = f"Hospital: {self.name}\nCode: {self.hospital_code}\nAddress: {self.address}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        qr_image.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)

        self.registration_qr.save(
            f'hospital_{self.hospital_code}_qr.png',
            File(qr_buffer),
            save=False
        )
        super().save(update_fields=['registration_qr'])
