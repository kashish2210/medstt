from django import forms
from .models import Hospital, Doctor, Nurse, Patient

class HospitalRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=200, label="Hospital Name")
    address = forms.CharField(widget=forms.Textarea)
    phone = forms.CharField(max_length=15)
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data

class DoctorRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=100)
    age = forms.IntegerField()
    phone = forms.CharField(max_length=15)
    speciality = forms.CharField(max_length=100)
    gender = forms.ChoiceField(choices=Doctor.GENDER_CHOICES)
    room_clinic_number = forms.CharField(max_length=20)
    hospital_code = forms.CharField(max_length=10, help_text="Enter hospital code to join")
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data

class NurseRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=15)
    age = forms.IntegerField()
    gender = forms.ChoiceField(choices=Nurse.GENDER_CHOICES)
    hospital_code = forms.CharField(max_length=10, help_text="Enter hospital code to join")
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data

class PatientRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=100)
    age = forms.IntegerField()
    phone = forms.CharField(max_length=15)
    gender = forms.ChoiceField(choices=Patient.GENDER_CHOICES)
    problem_diseases = forms.CharField(widget=forms.Textarea, label="Current Problems/Diseases")
    medicines_consumed = forms.CharField(widget=forms.Textarea, required=False, label="Current Medicines")
    medicine_countdown = forms.IntegerField(initial=0, label="Medicine Days Remaining")
    visibility = forms.ChoiceField(choices=Patient.VISIBILITY_CHOICES, label="Who can see your medical info?")
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data