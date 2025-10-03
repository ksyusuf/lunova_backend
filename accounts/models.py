# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator


class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    EXPERT = 'expert', 'Uzman'
    CLIENT = 'client', 'Danışan'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email adresi zorunludur')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=UserRole.choices)
    is_deleted = models.BooleanField(default=False)
    country = models.CharField(max_length=64, default="TR")
    national_id = models.CharField(max_length=64, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.ForeignKey('Gender', null=True, blank=True, on_delete=models.SET_NULL, related_name='users')
    id_number = models.CharField(
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message="TC Kimlik numarası 11 haneli olmalıdır ve sadece rakamlardan oluşmalıdır."
            )
        ]
    )
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_photo = models.ImageField(null=True, blank=True)
    
    # Username'i opsiyonel yap
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    timezone = models.CharField(
        max_length=64, 
        default="Europe/Istanbul",
        help_text="Kullanıcının varsayılan saat dilimi"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']
    
    objects = UserManager()


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    # Admin-specific fields (currently empty)


def expert_profile_photo_upload_path(instance, filename):
    return f"experts/{instance.user.id}/profile_photos/{filename}"

def expert_degree_upload_path(instance, filename):
    return f"experts/{instance.user.id}/degree/{filename}"

def client_profile_photo_upload_path(instance, filename):
    return f"clients/{instance.user.id}/profile_photos/{filename}"


# Service model
class Service(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# -----------------------------
# Gender
# -----------------------------
class Gender(models.Model):
    name = models.CharField(max_length=32, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# -----------------------------
# Abstract Base Profile
# -----------------------------
class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


# -----------------------------
# ExpertProfile
# -----------------------------
class ExpertProfile(BaseProfile):
    degree_file = models.FileField(upload_to=expert_degree_upload_path, null=True, blank=True)
    university = models.CharField(max_length=128, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    approval_status = models.BooleanField(default=False)
    services = models.ManyToManyField("Service", related_name="experts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.id_number or self.user.national_id})"


# -----------------------------
# ClientProfile
# -----------------------------
class AddictionType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ClientProfile(BaseProfile):
    received_service_before = models.BooleanField(default=False)
    substances_used = models.ManyToManyField(AddictionType, blank=True, related_name="clients")
    support_goal = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.id_number or self.user.national_id})"
