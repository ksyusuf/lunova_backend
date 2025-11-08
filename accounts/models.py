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
    id_number = models.CharField(max_length=11, unique=True, null=True, blank=True, validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message="TC Kimlik numarası 11 haneli olmalıdır ve sadece rakamlardan oluşmalıdır."
            )
        ]
    )
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    @property
    def profile_photo_url(self):
        """Kullanıcının profil fotoğrafını döndürür, yoksa cinsiyete göre varsayılanı verir."""
        photo_doc = self.documents.filter(type=DocumentType.PROFILE_PHOTO).first()  # type: ignore
        if photo_doc and photo_doc.file:
            return photo_doc.file.url

        gender_key = self.gender.name.lower() if self.gender else "neutral"
        default_photos = {
            "erkek": "/static/default_photos/male.png",
            "kadın": "/static/default_photos/female.png",
            "neutral": "/static/default_photos/neutral.png",
        }

        ### şeklinde bir düzenleme yapılmış olması gerekir.
        # / static / default_photos / male.png
        # / static / default_photos / female.png
        # / static / default_photos / neutral.png

        return default_photos.get(gender_key, default_photos["neutral"])

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
    university = models.ForeignKey("University", on_delete=models.SET_NULL, null=True, blank=True, related_name="experts")
    degree_level = models.ForeignKey("DegreeLevel", on_delete=models.SET_NULL, null=True, blank=True, related_name="experts")
    major = models.ForeignKey("Major", on_delete=models.SET_NULL, null=True, blank=True, related_name="experts")

    about = models.TextField(null=True, blank=True)
    approval_status = models.BooleanField(default=False)
    title = models.CharField(max_length=128, null=True, blank=True)  # Örn: Uzman Psikolog
    experience_years = models.PositiveIntegerField(null=True, blank=True)  # Deneyim yılı
    license_number = models.CharField(max_length=64, null=True, blank=True)
    institution = models.CharField(max_length=256, null=True, blank=True)

    session_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, default="TRY")
    appointment_duration = models.PositiveIntegerField(default=45, help_text="Dakika cinsinden seans süresi")
    free_first_session = models.BooleanField(default=False)

    video_intro_url = models.URLField(null=True, blank=True)
    availability_status = models.CharField(max_length=32, default="available", choices=[
        ("active", "Aktif"),
        ("available", "Müsait"),
        ("busy", "Meşgul"),
        ("away", "Tatilde")
    ])

    rating_average = models.FloatField(default=0)
    rating_count = models.PositiveIntegerField(default=0)

    # İlişkiler
    services = models.ManyToManyField("Service", related_name="experts", blank=True)
    specializations = models.ManyToManyField("Specialization", related_name="experts", blank=True)
    languages = models.ManyToManyField("Language", related_name="experts", blank=True)
    approach_methods = models.ManyToManyField("ApproachMethod", related_name="experts", blank=True)
    target_groups = models.ManyToManyField("TargetGroup", related_name="experts", blank=True)
    session_types = models.ManyToManyField("SessionType", related_name="experts", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.id_number or self.user.national_id})"


class DocumentType(models.TextChoices):
    PROFILE_PHOTO = "profile_photo", "Profil Fotoğrafı"
    DEGREE = "degree", "Diploma / Sertifika"
    CV = "cv", "Özgeçmiş"
    OTHER = "other", "Diğer"


def upload_document_path(instance, filename):
    user = instance.user
    doc_type = instance.type

    if doc_type == DocumentType.PROFILE_PHOTO:
        base_path = "experts" if user.role == "expert" else "clients"
        return f"{base_path}/{user.id}/profile_photos/{filename}"

    elif doc_type == DocumentType.DEGREE:
        return f"experts/{user.id}/degree/{filename}"

    elif doc_type == DocumentType.CV:
        return f"experts/{user.id}/cv/{filename}"

    else:
        return f"clients/{user.id}/documents/{filename}"


class Document(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(upload_to=upload_document_path)
    type = models.CharField(max_length=32, choices=DocumentType.choices)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)


class Language(models.Model):
    name = models.CharField(max_length=64, unique=True)
    code = models.CharField(max_length=10, unique=True)  # örn: "tr", "en"
    is_active = models.BooleanField(default=True)


class University(models.Model):
    name = models.CharField(max_length=128, unique=True)
    country = models.CharField(max_length=64, default="TR")


class DegreeLevel(models.Model):
    name = models.CharField(max_length=64, unique=True)  # Lisans, Yüksek Lisans, Doktora


class Major(models.Model):
    name = models.CharField(max_length=128, unique=True)  # Psikoloji, Psikiyatri vb.


class Specialization(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(null=True, blank=True)


class ApproachMethod(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(null=True, blank=True)


class TargetGroup(models.Model):
    name = models.CharField(max_length=64, unique=True)  # Ergen, Yetişkin, Aile
    description = models.TextField(null=True, blank=True)


class SessionType(models.Model):
    name = models.CharField(max_length=64, unique=True)  # Online, Yüz Yüze, Karma


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
