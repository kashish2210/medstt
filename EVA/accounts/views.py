from django.shortcuts import render, redirect, get_object_or_404
from .forms import DoctorRegistrationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import HttpResponse

def register_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect('accounts:doctor_queue')  # or wherever you want to go after registration
    else:
        form = DoctorRegistrationForm()

    return render(request, 'accounts/register_doctor.html', {'form': form})

# accounts/views.py

from .forms import HospitalRegistrationForm

def register_hospital(request):
    if request.method == 'POST':
        form = HospitalRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('accounts:hospital_dashboard')
    else:
        form = HospitalRegistrationForm()

    return render(request, 'accounts/register_hospital.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            if user.user_type == 'doctor':
                return redirect('accounts:doctor_queue')
            elif user.user_type == 'nurse':
                return redirect('accounts:nurse_queue')
            elif user.user_type == 'patient':
                return redirect('accounts:patient_dashboard')
            elif user.user_type == 'hospital':
                return redirect('accounts:hospital_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('accounts:login')  # or wherever you want to go after logout
    pass  # Implement your logout logic here
# accounts/views.py

from .forms import NurseRegistrationForm

def register_nurse(request):
    if request.method == 'POST':
        form = NurseRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('login')  # or your success page
    else:
        form = NurseRegistrationForm()
    return render(request, 'accounts/register_nurse.html', {'form': form})

# accounts/views.py

from .forms import PatientRegistrationForm

def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('login')  # or a custom success page
    else:
        form = PatientRegistrationForm()
    return render(request, 'accounts/register_patient.html', {'form': form})

# accounts/views.py or medical/views.py

from django.shortcuts import render, redirect
from .forms import MedicalCaseForm
from .models import PatientProfile, MedicalCase

from django.contrib.auth.decorators import login_required

@login_required
def create_medical_case(request):
    if request.method == 'POST':
        form = MedicalCaseForm(request.POST)
        if form.is_valid():
            medical_case = form.save(commit=False)
            medical_case.patient = request.user.patient_profile  # assumes 1-to-1 link from CustomUser
            medical_case.status = 'pending'  # default, but just to be safe
            medical_case.save()
            return redirect('accounts:patient_dashboard')  # or wherever you want to go after submission
    else:
        form = MedicalCaseForm()
    return render(request, 'accounts/create_case.html', {'form': form})

@login_required
def patient_dashboard(request):
    patient_profile = request.user.patient_profile
    cases = MedicalCase.objects.filter(patient=patient_profile).select_related('doctor__user', 'assigned_nurse__user')
    return render(request, 'accounts/patient_dashboard.html', {
        'user': request.user,
        'profile': patient_profile,
        'cases': cases,
    })

@login_required
def doctor_dashboard(request):
    return HttpResponse("Doctor Dashboard")

@login_required
def nurse_dashboard(request):
    return HttpResponse("Nurse Dashboard")

@login_required
def hospital_dashboard(request):
    return HttpResponse("Hospital Dashboard")
@login_required
def nurse_queue(request):
    nurse_queue = MedicalCase.objects.filter(
        assigned_nurse__isnull=True,
        status='pending'
    ).order_by('id')

    return render(request, 'accounts/nurse_queue.html', {'queue': nurse_queue})


from .forms import NurseCaseUpdateForm

@login_required
def nurse_pick_case_view(request, case_id):
    case = get_object_or_404(MedicalCase, id=case_id, assigned_nurse__isnull=True)

    # Ensure only nurse can access
    if request.user.user_type != 'nurse':
        return redirect('not_authorized')

    if request.method == 'POST':
        form = NurseCaseUpdateForm(request.POST, instance=case)
        if form.is_valid():
            updated_case = form.save(commit=False)
            updated_case.assigned_nurse = request.user.nurse_profile
            updated_case.status = 'in_progress'
            updated_case.save()
            return redirect('accounts:nurse_queue')  # or another dashboard
    else:
        form = NurseCaseUpdateForm(instance=case)

    return render(request, 'accounts/pick_case_form.html', {'form': form, 'case': case})

from .models import DoctorProfile
@login_required
def doctor_queue(request):
    doctor_profile = request.user.doctor_profile
    queue = doctor_profile.queue.all()
    return render(request, 'accounts/doctor_queue.html', {'queue': queue})

# Add this to your views.py file, replacing the existing hospital_dashboard function

@login_required
def hospital_dashboard(request):
    # Ensure user is a hospital
    if request.user.user_type != 'hospital':
        return redirect('accounts:login')
    
    try:
        hospital_profile = request.user.hospital_profile
        
        # Get counts
        doctors_count = hospital_profile.doctors.count()
        nurses_count = hospital_profile.nurses.count()
        rooms_count = hospital_profile.rooms.count()
        
        # Get hospital info
        hospital_name = request.user.name or "General Hospital"
        hospital_code = hospital_profile.hospital_code
        hospital_qr = hospital_profile.registration_qr.url if hospital_profile.registration_qr else None
        
        context = {
            'user': request.user,
            'hospital_profile': hospital_profile,
            'hospital_name': hospital_name,
            'hospital_code': hospital_code,
            'hospital_qr': hospital_qr,
            'doctors_count': doctors_count,
            'nurses_count': nurses_count,
            'rooms_count': rooms_count,
        }
        
        return render(request, 'accounts/hospital_dashboard.html', context)
        
    except Exception as e:
        # If hospital profile doesn't exist, create one
        if not hasattr(request.user, 'hospital_profile'):
            from .models import HospitalProfile
            HospitalProfile.objects.create(
                user=request.user,
                address="Default Address"
            )
            return redirect('accounts:hospital_dashboard')
        
        # For other errors, show a simple message
        return render(request, 'accounts/hospital_dashboard.html', {
            'user': request.user,
            'hospital_name': 'General Hospital',
            'hospital_code': 'N/A',
            'doctors_count': 0,
            'nurses_count': 0,
            'rooms_count': 0,
        })