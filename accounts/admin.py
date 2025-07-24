from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ExpertProfile, ClientProfile


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
    list_display = ('user', 'tc_kimlik', 'universite', 'gsm_no', 'uzmanlik_alani', 'onay_durumu')
    search_fields = ('user__email', 'tc_kimlik', 'universite', 'gsm_no')
    list_filter = ('uzmanlik_alani', 'onay_durumu')

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tc_kimlik', 'yas', 'cinsiyet', 'gsm_no', 'bagimlilik_turu', 'daha_once_hizmet_aldi_mi')
    search_fields = ('user__email', 'tc_kimlik', 'gsm_no')
    list_filter = ('cinsiyet', 'bagimlilik_turu', 'daha_once_hizmet_aldi_mi')
