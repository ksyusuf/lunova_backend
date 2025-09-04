from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ExpertProfile, ClientProfile, Gender


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Liste görünümünde gözükecek sütunlar
    list_display = ('email', 'role', 'is_staff', 'is_active')

    # Detay sayfasındaki alan grupları
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Ek Bilgiler", {"fields": ("role", )}),
    )
    search_fields = ('email',)


@admin.register(ExpertProfile)
class ExpertProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_id_number', 'university', 'get_phone_number', 'get_services', 'approval_status')
    search_fields = ('user__email', 'user__id_number', 'university', 'user__phone_number')
    list_filter = ('services', 'approval_status')

    def get_services(self, obj):
        return ", ".join([s.name for s in obj.services.all()])
    get_services.short_description = "Uzmanlık Alanları"

    def get_id_number(self, obj):
        return obj.user.id_number
    get_id_number.short_description = 'TC Kimlik'

    def get_phone_number(self, obj):
        return obj.user.phone_number
    get_phone_number.short_description = 'Telefon'


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_id_number', 'get_birth_date', 'get_gender', 'get_phone_number', 'get_substances_used', 'received_service_before')
    search_fields = ('user__email', 'user__id_number', 'user__phone_number')
    list_filter = ('substances_used', 'received_service_before')

    def get_substances_used(self, obj):
        return ", ".join([s.name for s in obj.substances_used.all()])
    get_substances_used.short_description = "Bağımlılık Türleri"

    def get_id_number(self, obj):
        return obj.user.id_number
    get_id_number.short_description = 'TC Kimlik'

    def get_birth_date(self, obj):
        return obj.user.birth_date
    get_birth_date.short_description = 'Doğum Tarihi'

    def get_gender(self, obj):
        return obj.user.gender_id
    get_gender.short_description = 'Cinsiyet'

    def get_phone_number(self, obj):
        return obj.user.phone_number
    get_phone_number.short_description = 'Telefon'


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
