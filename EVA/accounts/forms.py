# accounts/forms.py

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, HospitalProfile, NurseProfile, PatientProfile, MedicalCase

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'name','phone_number')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email','name', 'phone_number')

# accounts/forms.py

from django import forms
from .models import CustomUser, DoctorProfile, HospitalProfile
from django.contrib.auth.forms import UserCreationForm

class DoctorRegistrationForm(forms.ModelForm):
    # Fields for CustomUser
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    email = forms.EmailField(label="Email")
    name = forms.CharField(label="Full Name")
    phone_number = forms.CharField(label="Phone Number")

    # Fields for DoctorProfile
    birth_date = forms.DateField(label="Date of Birth", widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=DoctorProfile.GENDER_CHOICES, label="Gender")
    speciality = forms.CharField(label="Speciality")
    hospital_code = forms.CharField(label="Hospital Code")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'name', 'phone_number']

    def clean_hospital_code(self):
        code = self.cleaned_data.get('hospital_code')
        if not HospitalProfile.objects.filter(hospital_code=code).exists():
            raise forms.ValidationError("Invalid hospital code.")
        return code

    def save(self, commit=True):
        # Create user first
        user = CustomUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            name=self.cleaned_data['name'],
            phone_number=self.cleaned_data['phone_number'],
            user_type='doctor',
        )

        # Get linked hospital
        hospital = HospitalProfile.objects.get(hospital_code=self.cleaned_data['hospital_code'])

        # Create doctor profile
        DoctorProfile.objects.create(
            user=user,
            birth_date=self.cleaned_data['birth_date'],
            gender=self.cleaned_data['gender'],
            speciality=self.cleaned_data['speciality'],
            hospital=hospital,
        )

        return user
    
class HospitalRegistrationForm(forms.ModelForm):
    # CustomUser fields
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    email = forms.EmailField(label="Email")
    phone_number = forms.CharField(label="Phone Number")


    # HospitalProfile fields
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label="Hospital Address")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'name', 'phone_number']

    def save(self, commit=True):
        # Create the CustomUser
        user = CustomUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            phone_number=self.cleaned_data['phone_number'],
            user_type='hospital',
        )

        # Create the HospitalProfile
        HospitalProfile.objects.create(
            user=user,
            address=self.cleaned_data['address'],
        )

        return user


class NurseRegistrationForm(forms.ModelForm):
    # Fields from CustomUser
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    email = forms.EmailField(label="Email")
    phone_number = forms.CharField(label="Phone Number")

    # Fields from NurseProfile
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Date of Birth")
    gender = forms.ChoiceField(choices=NurseProfile.GENDER_CHOICES, label="Gender")
    hospital_code = forms.CharField(label="Hospital Code")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'name', 'phone_number']

    def clean_hospital_code(self):
        code = self.cleaned_data['hospital_code']
        if not HospitalProfile.objects.filter(hospital_code=code).exists():
            raise forms.ValidationError("Invalid hospital code.")
        return code

    def save(self, commit=True):
        # Create the CustomUser (name is handled here)
        user = CustomUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            phone_number=self.cleaned_data['phone_number'],
            name=self.cleaned_data['name'],
            user_type='nurse',
        )

        # Get hospital by code
        hospital = HospitalProfile.objects.get(hospital_code=self.cleaned_data['hospital_code'])

        # Create the NurseProfile
        NurseProfile.objects.create(
            user=user,
            birth_date=self.cleaned_data['birth_date'],
            gender=self.cleaned_data['gender'],
            hospital=hospital,
        )

        return user
    
class PatientRegistrationForm(forms.ModelForm):
    # Fields from CustomUser
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    email = forms.EmailField(label="Email")
    phone_number = forms.CharField(label="Phone Number")
    name = forms.CharField(label="Full Name")

    # Fields from PatientProfile
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), 
        label="Date of Birth"
    )
    gender = forms.ChoiceField(
        choices=PatientProfile.GENDER_CHOICES,
        label="Gender"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'name', 'phone_number']

    def save(self, commit=True):
        # Create CustomUser
        user = CustomUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            name=self.cleaned_data['name'],
            phone_number=self.cleaned_data['phone_number'],
            user_type='patient',
        )

        # Create PatientProfile
        PatientProfile.objects.create(
            user=user,
            birth_date=self.cleaned_data['birth_date'],
            gender=self.cleaned_data['gender']
        )

        return user

class MedicalCaseForm(forms.ModelForm):
    initial_problem = forms.CharField(
        label="Problem / Reason for visiting",
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your issue...'})
    )

    class Meta:
        model = MedicalCase
        fields = ['initial_problem']

class NurseCaseUpdateForm(forms.ModelForm):
    initial_nurse_notes = forms.CharField(
        label="Nurse's Notes",
        widget=forms.Textarea(attrs={'rows': 4}),
        required=True
    )
    doctor_queue = forms.ModelChoiceField(
        queryset=DoctorProfile.objects.all(),
        label="Assign to Doctor",
        required=True
    )

    class Meta:
        model = MedicalCase
        fields = ['initial_nurse_notes', 'doctor_queue']