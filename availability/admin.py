from django.contrib import admin
from .models import WeeklyAvailability, AvailabilityException


@admin.register(WeeklyAvailability)
class WeeklyAvailabilityAdmin(admin.ModelAdmin):
    list_display = [
        'expert', 'day_of_week', 'start_time', 'end_time', 
        'service', 'is_active', 'slot_minutes', 'capacity'
    ]
    list_filter = [
        'day_of_week', 'is_active', 'service', 'expert'
    ]
    search_fields = [
        'expert__user__first_name', 'expert__user__last_name',
        'expert__user__email'
    ]
    ordering = ['expert', 'day_of_week', 'start_time']
    
    fieldsets = (
        ('Uzman Bilgisi', {
            'fields': ('expert', 'service')
        }),
        ('Zaman Bilgisi', {
            'fields': ('day_of_week', 'start_time', 'end_time')
        }),
        ('Ayarlar', {
            'fields': ('is_active', 'slot_minutes', 'capacity')
        }),
    )


@admin.register(AvailabilityException)
class AvailabilityExceptionAdmin(admin.ModelAdmin):
    list_display = [
        'expert', 'date', 'exception_type', 'start_time', 
        'end_time', 'service', 'note'
    ]
    list_filter = [
        'exception_type', 'date', 'service', 'expert'
    ]
    search_fields = [
        'expert__user__first_name', 'expert__user__last_name',
        'expert__user__email', 'note'
    ]
    ordering = ['expert', 'date']
    
    fieldsets = (
        ('Uzman Bilgisi', {
            'fields': ('expert', 'service')
        }),
        ('İstisna Bilgisi', {
            'fields': ('date', 'exception_type', 'start_time', 'end_time')
        }),
        ('Ek Bilgiler', {
            'fields': ('note',)
        }),
    )
