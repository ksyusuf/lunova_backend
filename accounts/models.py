# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
import uuid
from django.db.models import Q


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


# Gender
class GenderChoices(models.TextChoices):
    MALE = 'male', 'Erkek'
    FEMALE = 'female', 'Kadın'
    OTHER = 'other', 'Diğer'
    PREFER_NOT_TO_SAY = 'pn2s', 'Belirtmek İstemiyor'


class User(AbstractUser):
    email = models.EmailField("E-posta adresi", unique=True)
    role = models.CharField("Rol", max_length=10, choices=UserRole.choices)
    is_deleted = models.BooleanField("Silindi mi?", default=False)
    country = models.CharField("Ülke", max_length=64, default="TR")
    national_id = models.CharField("Ulusal Kimlik Numarası", max_length=64, null=True, blank=True)
    birth_date = models.DateField("Doğum Tarihi", null=True, blank=True)
    gender = models.CharField("Cinsiyet", max_length=10, choices=GenderChoices.choices, null=True, blank=True)
    id_number = models.CharField(
        "TC Kimlik Numarası",
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
    phone_number = models.CharField("Telefon Numarası", max_length=20, null=True, blank=True)
    username = models.CharField("Kullanıcı Adı", max_length=150, unique=True, null=True, blank=True)
    timezone = models.CharField("Saat Dilimi", max_length=64, default="Europe/Istanbul",
                                help_text="Kullanıcının varsayılan saat dilimi")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']
    
    objects = UserManager()

    def __str__(self):
        return self.get_full_name() or self.email

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    # Admin-specific fields (currently empty)

    def __str__(self):
        return f"Admin: {self.user.get_full_name()}"

    class Meta:
        verbose_name = "Yönetici Profili"
        verbose_name_plural = "Yönetici Profilleri"


# Service model
class Service(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Hizmet"
        verbose_name_plural = "Hizmetler"


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
    about = models.TextField("Hakkında", null=True, blank=True)
    approval_status = models.BooleanField("Onay Durumu", default=False)
    title = models.CharField("Unvan", max_length=128, null=True, blank=True)
    experience_years = models.PositiveIntegerField("Deneyim Yılı", null=True, blank=True)
    license_number = models.CharField("Lisans Numarası", max_length=64, null=True, blank=True)
    institution = models.CharField("Kurum", max_length=256, null=True, blank=True)
    session_price = models.DecimalField("Seans Ücreti", max_digits=8, decimal_places=2, null=True, blank=True)
    currency = models.CharField("Para Birimi", max_length=8, default="TRY")
    appointment_duration = models.PositiveIntegerField("Seans Süresi (dk)", default=45)
    free_first_session = models.BooleanField("İlk Seans Ücretsiz mi?", default=False)
    video_intro_url = models.URLField("Tanıtım Videosu URL'si", null=True, blank=True)
    availability_status = models.CharField("Müsaitlik Durumu", max_length=32, default="available", choices=[
        ("available", "Müsait"),
        ("active", "Aktif"),
        ("busy", "Meşgul"),
        ("away", "Tatilde")
    ])
    rating_average = models.FloatField("Ortalama Puan", default=0)
    rating_count = models.PositiveIntegerField("Puan Sayısı", default=0)

    # İlişkiler
    university = models.ForeignKey("University", verbose_name="Üniversite", on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name="experts")
    degree_level = models.ForeignKey("DegreeLevel", verbose_name="Eğitim Düzeyi", on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name="experts")
    major = models.ForeignKey("Major", verbose_name="Bölüm", on_delete=models.SET_NULL,
                              null=True, blank=True, related_name="experts")
    services = models.ManyToManyField("Service", verbose_name="Hizmetler", related_name="experts", blank=True)
    specializations = models.ManyToManyField("Specialization", verbose_name="Uzmanlık Alanları",
                                             related_name="experts", blank=True)
    languages = models.ManyToManyField("Language", verbose_name="Diller", related_name="experts", blank=True)
    approach_methods = models.ManyToManyField("ApproachMethod", verbose_name="Yaklaşım Yöntemleri",
                                              related_name="experts", blank=True)
    target_groups = models.ManyToManyField("TargetGroup", verbose_name="Hedef Gruplar",
                                           related_name="experts", blank=True)
    session_types = models.ManyToManyField("SessionType", verbose_name="Seans Türleri",
                                           related_name="experts", blank=True)

    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.id_number or self.user.national_id})"

    class Meta:
        verbose_name = "Uzman Profili"
        verbose_name_plural = "Uzman Profilleri"


class DocumentType(models.TextChoices):
    PROFILE_PHOTO = "profile_photo", "Profil Fotoğrafı"
    DEGREE = "degree", "Diploma / Sertifika"
    CV = "cv", "Özgeçmiş"
    CONSENT_FORM = "consent_form", "Onay Formu"
    OTHER = "other", "Diğer"


def upload_document_path(instance, filename):
    user = instance.user
    doc_type = instance.type
    print("User.id: ", user.id)
    role_path = "experts" if user.role == UserRole.EXPERT else "clients"
    
    # 2. Dosya ismini benzersiz yap (UUID kullanarak çakışmayı önle)
    ext = filename.split('.')[-1]
    unique_filename = f"{instance.uid}.{ext}"
    
    return f"{role_path}/{user.id}/{doc_type}/{unique_filename}"


class Document(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="documents")
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    file_key = models.CharField(max_length=255, unique=True)
    original_filename = models.CharField(max_length=255)
    type = models.CharField(max_length=32, choices=DocumentType.choices)
    is_primary = models.BooleanField("Birincil mi?", default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_type_display()}"
    
    def save(self, *args, **kwargs):
        # Eğer bu dosya primary olarak set edildiyse, 
        # aynı kullanıcı ve aynı tipteki diğer dosyaların primary özelliğini kaldır.
        if self.is_primary:
            Document.objects.filter(
                user=self.user, 
                type=self.type, 
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Belge"
        verbose_name_plural = "Belgeler"
        constraints = [
        models.CheckConstraint(
            condition=Q(is_primary=False) | Q(is_current=True),
            name="primary_must_be_current",
        ),
    ]


class Language(models.Model):
    name = models.CharField(max_length=64, unique=True)
    code = models.CharField(max_length=10, unique=True)  # örn: "tr", "en"
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Dil"
        verbose_name_plural = "Diller"


class University(models.Model):
    name = models.CharField(max_length=128, unique=True)
    country = models.CharField(max_length=64, default="TR")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Üniversite"
        verbose_name_plural = "Üniversiteler"


class DegreeLevel(models.Model):
    name = models.CharField(max_length=64, unique=True)  # Lisans, Yüksek Lisans, Doktora

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Eğitim Düzeyi"
        verbose_name_plural = "Eğitim Düzeyleri"


class Major(models.Model):
    name = models.CharField(max_length=128, unique=True)  # Psikoloji, Psikiyatri vb.

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Bölüm"
        verbose_name_plural = "Bölümler"


class Specialization(models.Model):
    name = models.CharField(max_length=128, unique=True)  # Örnekler: Bağımlılık Terapisi, Travma Odaklı Terapi

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Uzmanlık Alanı"
        verbose_name_plural = "Uzmanlık Alanları"


class ApproachMethod(models.Model):
    name = models.CharField(max_length=128, unique=True)
    # Örnekler: Bilişsel Davranışçı Terapi (BDT), Kabul ve Kararlılık Terapisi (ACT)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Yaklaşım Yöntemi"
        verbose_name_plural = "Yaklaşım Yöntemleri"


class TargetGroup(models.Model):
    name = models.CharField(max_length=64, unique=True)  # Ergen, Yetişkin, Aile

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Hedef Grup"
        verbose_name_plural = "Hedef Gruplar"


class SessionType(models.Model):
    name = models.CharField(max_length=64, unique=True)  # Online, Yüz Yüze, Karma

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Seans Türü"
        verbose_name_plural = "Seans Türleri"


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

    class Meta:
        verbose_name = "Bağımlılık Türü"
        verbose_name_plural = "Bağımlılık Türleri"


class ClientProfile(BaseProfile):
    expert = models.ForeignKey('ExpertProfile', verbose_name="Atanan Uzman",
                               on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_clients')
    substances_used = models.ManyToManyField('AddictionType', verbose_name="Bağımlılık Türleri",
                                             blank=True, related_name="clients")
    support_goal = models.TextField("Destek Hedefi", null=True, blank=True)
    received_service_before = models.BooleanField("Daha Önce Hizmet Aldı mı?", default=False)
    onboarding_complete = models.BooleanField("Profilini Tamamladı mı?", default=False)
    is_active_in_treatment = models.BooleanField("Tedavi Aktif mi?", default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.id_number or self.user.national_id})"

    class Meta:
        verbose_name = "Danışan Profili"
        verbose_name_plural = "Danışan Profilleri"


class EmergencyContact(models.Model):
    """
    Danışanın acil durumda ulaşılabilecek kişi/kurum bilgilerini tutar.
    Her danışan için birden fazla kayıt oluşturulabilir.
    """
    client_profile = models.ForeignKey(
        'ClientProfile',
        on_delete=models.CASCADE,
        related_name='emergency_contacts',
        help_text="İlgili acil durum iletişiminin ait olduğu danışan profili."
    )

    name = models.CharField(
        max_length=128,
        help_text="Acil durum iletişim kişisinin tam adı."
    )
    phone_number = models.CharField(
        max_length=20,
        help_text="Acil durum iletişim kişisinin telefon numarası."
    )

    # Kişinin danışanla ilişkisini belirten alan
    relationship = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="Danışanla olan akrabalık veya yakınlık derecesi (Örn: Eş, Anne, Kardeş, Vasi)."
    )

    # Birden fazla kişi varsa hangisinin birincil olduğunu belirten alan
    is_primary = models.BooleanField(
        default=False,
        help_text="Bu kişinin birincil (ilk aranacak) acil durum kişisi olup olmadığı."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Acil Durum İletişimi"
        verbose_name_plural = "Acil Durum İletişimleri"

    def __str__(self):
        return f"Acil İletişim: {self.name} ({self.client_profile.user.get_full_name()})"

    class Meta:
        verbose_name = "Acil Durum Kişisi"
        verbose_name_plural = "Acil Durum Kişileri"
