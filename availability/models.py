from django.db import models
from accounts.models import ExpertProfile, Service


# -----------------------------
# Weekly Availability (tekrarlayan program)
# -----------------------------
class WeeklyAvailability(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, 'Pazartesi'
        TUESDAY = 1, 'Salı'
        WEDNESDAY = 2, 'Çarşamba'
        THURSDAY = 3, 'Perşembe'
        FRIDAY = 4, 'Cuma'
        SATURDAY = 5, 'Cumartesi'
        SUNDAY = 6, 'Pazar'

    expert = models.ForeignKey(
        ExpertProfile,
        on_delete=models.CASCADE,
        related_name="weekly_availabilities"
    )
    day_of_week = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Timezone artık ExpertProfile içinde tanımlı olmalı
    # Buradan erişeceksin: expert.timezone

    service = models.ForeignKey(
        Service,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="weekly_availabilities"
    )

    is_active = models.BooleanField(default=True)
    slot_minutes = models.PositiveIntegerField(default=50)
    capacity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_time__lt=models.F("end_time")),
                name="weekly_availability_start_before_end",
            ),
            # Çakışmayı engelle: aynı gün + aynı uzman + aynı servis için
            models.UniqueConstraint(
                fields=["expert", "day_of_week", "service", "start_time", "end_time"],
                name="unique_expert_service_day_time",
            ),
        ]

    def __str__(self):
        return f"{self.expert.user.get_full_name()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


# -----------------------------
# Availability Exceptions (istisnalar)
# -----------------------------
class AvailabilityException(models.Model):
    expert = models.ForeignKey(
        ExpertProfile,
        on_delete=models.CASCADE,
        related_name="availability_exceptions"
    )
    date = models.DateField()

    # İki senaryo:
    # 1) "cancel" → mevcut haftalık müsaitlik iptal edilir (opsiyonel saat aralığı ile)
    # 2) "add"    → o güne ekstra müsaitlik eklenir
    EXCEPTION_TYPE_CHOICES = [
        ("cancel", "İptal"),
        ("add", "Ekstra"),
    ]
    exception_type = models.CharField(max_length=10, choices=EXCEPTION_TYPE_CHOICES)

    # "add" tipinde zorunlu, "cancel" tipinde opsiyonel
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    service = models.ForeignKey(
        Service,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="availability_exceptions"
    )

    note = models.CharField(max_length=255, null=True, blank=True)

    # Tekrarlayan istisna desteği (örn: her yıl 1 Ocak kapalı)
    is_recurring = models.BooleanField(default=False)  # True = her yıl tekrarla

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Availability Exception"
        verbose_name_plural = "Availability Exceptions"
        indexes = [
            models.Index(fields=["expert", "date"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(exception_type="add", start_time__isnull=False, end_time__isnull=False)
                    | models.Q(exception_type="cancel")
                ),
                name="exception_type_time_validation",
            ),
            models.CheckConstraint(
                check=models.Q(start_time__lt=models.F("end_time")) | models.Q(start_time__isnull=True),
                name="exception_start_before_end",
            ),
        ]

    def __str__(self):
        return f"{self.expert.user.get_full_name()} - {self.date} ({self.exception_type})"


# -----------------------------
# AppointmentSlot (opsiyonel, pre-generated slotlar için)
# -----------------------------
class AppointmentSlot(models.Model):
    expert = models.ForeignKey(
        ExpertProfile,
        on_delete=models.CASCADE,
        related_name="appointment_slots"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="appointment_slots"
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["expert", "date"]),
        ]
        unique_together = ("expert", "service", "date", "start_time", "end_time")

    def __str__(self):
        return f"{self.expert.user.get_full_name()} - {self.date} {self.start_time}-{self.end_time}"
