from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'expert', 'client', 'date', 'time', 'duration', 
        'status', 'is_confirmed', 'created_at'
    ]
    list_filter = [
        'status', 'is_confirmed', 'date', 'expert', 'client'
    ]
    search_fields = [
        'expert__first_name', 'expert__last_name',
        'client__first_name', 'client__last_name'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Randevu Bilgileri', {
            'fields': ('expert', 'client', 'date', 'time', 'duration')
        }),
        ('Durum', {
            'fields': ('status', 'is_confirmed', 'notes')
        }),
        ('Zoom Bilgileri', {
            'fields': ('zoom_start_url', 'zoom_join_url', 'zoom_meeting_id'),
            'classes': ('collapse',)
        }),
        ('Sistem', {
            'fields': ('is_deleted', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
