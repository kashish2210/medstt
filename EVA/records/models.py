from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image

# Custom User Model
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('hospital', 'Hospital'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('nurse', 'Nurse'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"

# Hospital Model
class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile')
    name = models.CharField(max_length=200)
    address = models.TextField()
    hospital_code = models.CharField(max_length=10, unique=True, editable=False)
    registration_qr = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.hospital_code:
            self.hospital_code = str(uuid.uuid4())[:8].upper()
        
        super().save(*args, **kwargs)
        
        # Generate QR code
        if not self.registration_qr:
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
            super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

# Doctor Model
class Doctor(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone = models.CharField(max_length=15)
    speciality = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    room_clinic_number = models.CharField(max_length=20)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctors', null=True, blank=True)
    hospital_code = models.CharField(max_length=10, help_text="Enter hospital code to join")
    
    def save(self, *args, **kwargs):
        if self.hospital_code and not self.hospital:
            try:
                hospital = Hospital.objects.get(hospital_code=self.hospital_code)
                self.hospital = hospital
            except Hospital.DoesNotExist:
                pass
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Dr. {self.name} - {self.speciality}"

# Nurse Model
class Nurse(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nurse_profile')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='nurses', null=True, blank=True)
    hospital_code = models.CharField(max_length=10, help_text="Enter hospital code to join")
    
    def save(self, *args, **kwargs):
        if self.hospital_code and not self.hospital:
            try:
                hospital = Hospital.objects.get(hospital_code=self.hospital_code)
                self.hospital = hospital
            except Hospital.DoesNotExist:
                pass
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Nurse {self.name}"

# Patient Model
class Patient(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    VISIBILITY_CHOICES = (
        ('all', 'All Doctors'),
        ('specific', 'Specific Doctors Only'),
        ('none', 'No One (Cured)'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    problem_diseases = models.TextField()
    medicines_consumed = models.TextField(blank=True, null=True)
    medicine_countdown = models.IntegerField(default=0, help_text="Days remaining for medicine")
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='all')
    specific_doctors = models.ManyToManyField(Doctor, blank=True, related_name='accessible_patients')
    
    def __str__(self):
        return f"Patient {self.name}"

# Room Model
class Room(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='rooms')
    floor = models.IntegerField()
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50, default="General")
    is_occupied = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Room {self.room_number} - Floor {self.floor}"

# Queue Model
class Queue(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='queues')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    queue_number = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['doctor', 'queue_number', 'date_added']
    
    def __str__(self):
        return f"Queue {self.queue_number} - Dr. {self.doctor.name} - {self.patient.name}"

# Medical Case Model
class MedicalCase(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('cured', 'Cured'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_cases')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='cases')
    case_title = models.CharField(max_length=200)
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Case: {self.case_title} - {self.patient.name}"

# Medical Record Model
class MedicalRecord(models.Model):
    case = models.ForeignKey(MedicalCase, on_delete=models.CASCADE, related_name='records')
    consultation_date = models.DateTimeField(auto_now_add=True)
    symptoms = models.TextField()
    diagnosis = models.TextField()
    prescription = models.TextField()
    next_followup = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Record - {self.case.case_title} - {self.consultation_date.date()}"