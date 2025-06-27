from django.db import models

# Create your models here.
class Transcription(models.Model):
    identifier = models.CharField()
    data = models.JSONField()