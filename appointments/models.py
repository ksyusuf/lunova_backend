from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Appointment(models.Model):
    expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments_as_expert")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments_as_client")

    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(default=45)

    is_confirmed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Beklemede'),                   # uzman tarafından oluşturuldu, onay bekliyor
            ('waiting_approval', 'Onay Bekliyor'),     # danışan tarafından oluşturuldu
            ('confirmed', 'Onaylandı'),
            ('cancel_requested', 'İptal Talep Edildi'),# danışan iptal istedi
            ('cancelled', 'İptal Edildi'),
            ('completed', 'Tamamlandı'),
        ],
        default='pending'
    )

    # Zoom entegrasyonu için alanlar (opsiyonel)
    zoom_start_url = models.URLField(max_length=1000, null=True, blank=True)
    zoom_join_url = models.URLField(max_length=500, null=True, blank=True)
    zoom_meeting_id = models.CharField(max_length=128, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'appointments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.expert.get_full_name()} - {self.client.get_full_name()} ({self.date})"