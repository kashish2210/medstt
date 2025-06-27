from django.db import models
from django.conf import settings
import uuid

def generate_uid():
    return str(uuid.uuid4())

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        null=True,  # ✅ Optional for OTP
        blank=True
    )
    phone_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=100, null=True, blank=True)
    uid = models.CharField(default=generate_uid, max_length=200)

    def __str__(self):
        return self.phone_number
