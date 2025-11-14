from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, ExpertProfile, ClientProfile, EmergencyContact, Service, Language,
    University, DegreeLevel, Major, Specialization, ApproachMethod,
    TargetGroup, SessionType, AddictionType, AdminProfile, Document
)


# ====================================================================
# I. İÇ İLİŞKİLİ MODELLER (Alt tablolar)
# ====================================================================

class EmergencyContactInline(admin.TabularInline):
    """Danışan profil sayfasında acil iletişim bilgilerini alt tablo olarak gösterir."""
    model = EmergencyContact
    extra = 1
    fields = ('name', 'phone_number', 'relationship', 'is_primary')
    verbose_name = "Acil Durum Kişisi"
    verbose_name_plural = "Acil Durum Kişileri"


# ====================================================================
# II. KULLANICI YÖNETİMİ
# ====================================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Liste görünümü
    list_display = ('email', 'role', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'is_deleted')
    search_fields = ('email', 'first_name', 'last_name', 'id_number')
    ordering = ('email',)

    # Detay sayfası alan grupları
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Proje Bilgileri", {"fields": ("role", "is_deleted", "timezone")}),
        ("Ek Kişisel Bilgiler",
         {"fields": ("country", "national_id", "id_number", "birth_date", "gender", "phone_number")}),
    )

    verbose_name = "Kullanıcı"
    verbose_name_plural = "Kullanıcılar"


# ====================================================================
# III. PROFİL YÖNETİMİ
# ====================================================================

@admin.register(ExpertProfile)
class ExpertProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'get_full_name', 'title', 'experience_years',
        'approval_status', 'rating_average', 'get_services_short'
    )
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'title', 'license_number'
    )
    list_filter = ('approval_status', 'services', 'specializations', 'availability_status')

    fieldsets = (
        ("Kullanıcı ve Onay Bilgileri", {"fields": ('user', 'title', 'approval_status')}),
        ("Temel Bilgiler", {"fields": (
            'university', 'degree_level', 'major', 'experience_years',
            'license_number', 'institution', 'about'
        )}),
        ("Seans ve Ücret Bilgileri", {"fields": (
            'session_price', 'currency', 'appointment_duration',
            'free_first_session', 'availability_status', 'video_intro_url'
        )}),
        ("Puanlama Bilgileri", {"fields": ('rating_average', 'rating_count')}),
    )

    filter_horizontal = (
        'services', 'specializations', 'languages',
        'approach_methods', 'target_groups', 'session_types'
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Ad Soyad'

    def get_services_short(self, obj):
        services = obj.services.all()
        return ", ".join([s.name for s in services[:3]]) + ("..." if services.count() > 3 else "")
    get_services_short.short_description = "Hizmetler"

    verbose_name = "Uzman Profili"
    verbose_name_plural = "Uzman Profilleri"


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'expert', 'get_full_name', 'get_birth_date', 'get_gender',
        'get_phone_number', 'is_active_in_treatment', 'onboarding_complete'
    )

    fieldsets = (
        ("Temel Bilgiler", {"fields": ('user', 'expert', 'support_goal')}),
        ("Süreç ve Durum", {"fields": (
            'onboarding_complete', 'is_active_in_treatment', 'received_service_before'
        )}),
        ("Bağımlılık Bilgileri", {"fields": ('substances_used',)}),
    )

    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'expert__user__email'
    )
    list_filter = (
        'expert', 'is_active_in_treatment', 'onboarding_complete',
        'received_service_before', 'substances_used'
    )
    filter_horizontal = ('substances_used',)
    inlines = [EmergencyContactInline]

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Ad Soyad'

    def get_birth_date(self, obj):
        return obj.user.birth_date
    get_birth_date.short_description = 'Doğum Tarihi'

    def get_gender(self, obj):
        return obj.user.get_gender_display()
    get_gender.short_description = 'Cinsiyet'

    def get_phone_number(self, obj):
        return obj.user.phone_number
    get_phone_number.short_description = 'Telefon'

    verbose_name = "Danışan Profili"
    verbose_name_plural = "Danışan Profilleri"


# ====================================================================
# IV. DİĞER MODELLERİN YÖNETİMİ
# ====================================================================

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_profile', 'phone_number', 'relationship', 'is_primary')
    list_filter = ('is_primary', 'relationship')
    search_fields = ('name', 'phone_number', 'client_profile__user__email')
    verbose_name = "Acil Durum Kişisi"
    verbose_name_plural = "Acil Durum Kişileri"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'uploaded_at', 'verified')
    list_filter = ('type', 'verified')
    search_fields = ('user__email', 'type')
    readonly_fields = ('uploaded_at',)
    verbose_name = "Belge"
    verbose_name_plural = "Belgeler"


# ====================================================================
# V. DİĞER YARDIMCI MODELLER (Basit Yönetim)
# ====================================================================

admin.site.register(AdminProfile)
admin.site.register(Service)
admin.site.register(Language)
admin.site.register(University)
admin.site.register(DegreeLevel)
admin.site.register(Major)
admin.site.register(Specialization)
admin.site.register(ApproachMethod)
admin.site.register(TargetGroup)
admin.site.register(SessionType)
admin.site.register(AddictionType)
