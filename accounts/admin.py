from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Liste görünümünde gözükecek sütunlar
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')

    # Detay sayfasındaki alan grupları
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Ek Bilgiler", {"fields": ("role", "phone", "is_email_verified")}),
    )
