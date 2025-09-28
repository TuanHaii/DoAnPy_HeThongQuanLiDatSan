from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)

class Fieid(models.Model):
    SPORT_CHOICE = [
        ('football', 'Bong da',),
        ('badminton', 'Cau long',),
        ('basketball', 'Bong ro',),
        ('volleyball', 'Cau long',)
    ]
    name = models.CharField(max_length=255)
