# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    EXPERT = 'expert', 'Uzman'
    CLIENT = 'client', 'Danışan'


class User(AbstractUser):
    role = models.CharField(max_length=10, choices=UserRole.choices)


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    # Admin özel alanları (şimdilik boş)


def expert_profile_photo_upload_path(instance, filename):
    return f"experts/{instance.user.id}/profile_photos/{filename}"

def expert_diploma_upload_path(instance, filename):
    return f"experts/{instance.user.id}/diplomas/{filename}"

def client_profile_photo_upload_path(instance, filename):
    return f"clients/{instance.user.id}/profile_photos/{filename}"

class ExpertProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='expert_profile')
    tc_kimlik = models.CharField(max_length=11)
    diploma_dosyasi = models.FileField(upload_to=expert_diploma_upload_path, null=True, blank=True)
    universite = models.CharField(max_length=128, null=True, blank=True)
    gsm_no = models.CharField(max_length=20, null=True, blank=True)
    UZMANLIK_ALANI_CHOICES = [
        ('bilişsel terapi', 'Bilişsel Terapi'),
        ('aile terapisi', 'Aile Terapisi'),
        ('çocuk ve ergen', 'Çocuk ve Ergen'),
        ('diğer', 'Diğer'),
    ]
    uzmanlik_alani = models.CharField(max_length=64, choices=UZMANLIK_ALANI_CHOICES, null=True, blank=True)
    hakkinda = models.TextField(null=True, blank=True)
    onay_durumu = models.BooleanField(default=False)
    profil_fotografi = models.ImageField(upload_to=expert_profile_photo_upload_path, null=True, blank=True)


CINSIYET_CHOICES = [
    ('kadın', 'Kadın'),
    ('erkek', 'Erkek'),
    ('diğer', 'Diğer'),
    ('belirtmek istemiyorum', 'Belirtmek istemiyorum'),
]
BAGIMLILIK_TURU_CHOICES = [
    ('alkol', 'Alkol'),
    ('madde', 'Madde'),
    ('dijital', 'Dijital'),
    ('kumar', 'Kumar'),
    ('diğer', 'Diğer'),
]

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    tc_kimlik = models.CharField(max_length=11)
    daha_once_hizmet_aldi_mi = models.BooleanField(default=False)
    kullandigi_maddeler = models.TextField(null=True, blank=True)
    bagimlilik_turu = models.CharField(max_length=32, choices=BAGIMLILIK_TURU_CHOICES, null=True, blank=True)
    destek_amaci = models.TextField(null=True, blank=True)
    yas = models.IntegerField(null=True, blank=True)
    cinsiyet = models.CharField(max_length=32, choices=CINSIYET_CHOICES, null=True, blank=True)
    gsm_no = models.CharField(max_length=20, null=True, blank=True)
    profil_fotografi = models.ImageField(upload_to=client_profile_photo_upload_path, null=True, blank=True)