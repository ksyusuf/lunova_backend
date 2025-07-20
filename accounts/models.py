# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('expert', 'Uzman'),
        ('client', 'Danışan'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    # Admin özel alanları (şimdilik boş)

class ExpertProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='expert_profile')
    tc_kimlik = models.CharField(max_length=11)

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    tc_kimlik = models.CharField(max_length=11)