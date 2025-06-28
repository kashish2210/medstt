from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPES = [
        ('hospital', 'Hospital'),
        ('patient', 'Patient'),
        ('nurse', 'Nurse'),
        ('doctor', 'Doctor'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='patient')
    name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.user_type})"

class DoctorProfile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    speciality = models.CharField(max_length=100)
    hospital = models.ForeignKey('HospitalProfile', on_delete=models.SET_NULL, null=True, related_name='doctors')

    def __str__(self):
        return f"Dr. {self.user.name}"


class NurseProfile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='nurse_profile')
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    hospital = models.ForeignKey('HospitalProfile', on_delete=models.SET_NULL, null=True, related_name='nurses')

    def __str__(self):
        return f"Nurse {self.name}"

import uuid
import qrcode
from io import BytesIO
from django.core.files import File

class HospitalProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='hospital_profile')
    address = models.TextField()
    hospital_code = models.CharField(max_length=10, unique=True, editable=False)
    registration_qr = models.ImageField(upload_to='qr_codes/', blank=True)

    def save(self, *args, **kwargs):
        if not self.hospital_code:
            self.hospital_code = str(uuid.uuid4()).split('-')[0].upper()

        if not self.registration_qr:
            qr = qrcode.make(f"Hospital: {self.user.name}, Code: {self.hospital_code}")
            buffer = BytesIO()
            qr.save(buffer)
            filename = f"{self.user.name}_QR.png"
            self.registration_qr.save(filename, File(buffer), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.hospital_code

class Room(models.Model):
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='rooms')
    floor = models.IntegerField()
    room_number = models.CharField(max_length=10)
    doctor_assigned = models.OneToOneField(DoctorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='room')

    def __str__(self):
        return f"Room {self.room_number} - Floor {self.floor} ({self.hospital.name})"
    
class PatientProfile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)


    def __str__(self):
        return self.name

class Illness(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='illnesses')
    illness_name = models.CharField(max_length=255)
    until = models.DateField(null=True, blank=True)

class Medicine(models.Model):
    name= models.CharField(max_length=255)
    illness = models.ForeignKey(Illness, on_delete=models.CASCADE, related_name='medicines')

class MedicalRecord(models.Model):
    record = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    medical_case = models.ForeignKey('MedicalCase', on_delete=models.CASCADE, related_name='records')

class MedicalCase(models.Model):
    initial_problem = models.TextField(default='empty')
    initial_nurse_notes = models.TextField(default='empty')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_cases')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True, blank=True)
    doctor_queue = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='queue')
    assigned_nurse = models.ForeignKey(
        NurseProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_cases'
    )

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

class NurseQueue(models.Model):
    medical_case = models.ForeignKey(MedicalCase, on_delete=models.CASCADE, related_name='nurse_queue')

    def __str__(self):
        return f"Nurse {self.nurse.name} - Patient {self.patient.name} ({self.status})"


