# availability/scripts/seed_availability.py
"""
Bu script, veritabanındaki tüm uzmanlar (Expert) için çeşitli haftalık müsaitlik (WeeklyAvailability) ve istisnai durum (AvailabilityException) kayıtları oluşturur.
Test ortamında kullanılmak üzere tasarlanmıştır.
"""

import random
from datetime import datetime, timedelta, time
from django.db import IntegrityError
from availability.models import WeeklyAvailability, AvailabilityException
from accounts.models import ExpertProfile, Service


def create_availability_and_exceptions():
    """
    Veritabanına test verisi ekler.
    Bu fonksiyonu 'python manage.py runscript availability.scripts.feed_availability' ile çalıştırın.
    """
    # Tüm uzmanları al
    experts = ExpertProfile.objects.all()
    now = datetime.now()

    if not experts:
        print("Uyarı: Hiç uzman bulunamadı. Lütfen önce uzman ekleyin.")
        return

    created_count = 0
    skipped_count = 0

    for expert in experts:
        # Uzmanın hizmet ettiği servisleri al
        expert_services = list(expert.services.all())
        if not expert_services:
            # Eğer uzman servisi yoksa, tüm servislerden rastgele seç
            expert_services = list(Service.objects.all())

        # Her uzman için 5-10 farklı müsaitlik oluştur
        num_availabilities = random.randint(5, 10)

        for i in range(num_availabilities):
            # Haftanın gününü rastgele seç
            day_of_week = random.randint(0, 6)
            # Saat aralığını rastgele seç (08:00-18:00 arası)
            start_hour = random.randint(8, 16)
            start_time = time(hour=start_hour, minute=0)
            # 1-3 saatlik seans
            duration_hours = random.randint(1, 3)
            end_time = (datetime.combine(now.date(), start_time) + timedelta(hours=duration_hours)).time()

            # Uzmanın servislerinden rastgele seç
            service = random.choice(expert_services) if expert_services else None

            try:
                WeeklyAvailability.objects.create(
                    expert=expert,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    service=service,
                    is_active=True,
                    slot_minutes=50,  # Default slot süresi
                    capacity=1
                )
                created_count += 1
            except IntegrityError:
                # Tekrar eden kayıt varsa, pas geç
                skipped_count += 1
                continue
        
        # Her uzman için 5 istisnai durum oluştur, gelecek 3 aya serpiştir
        for j in range(5):
            days_ahead = random.randint(0, 89)  # 0-89 gün arası (yaklaşık 3 ay)
            exc_date = now.date() + timedelta(days=days_ahead)
            
            exception_type = random.choice(['cancel', 'add'])
            start_time = None
            end_time = None
            
            if exception_type == 'add':
                start_time = time(hour=random.randint(9, 17), minute=0)
                end_time = (datetime.combine(exc_date, start_time) + timedelta(hours=1)).time()
            
            AvailabilityException.objects.create(
                expert=expert,
                date=exc_date,
                start_time=start_time,
                end_time=end_time,
                exception_type=exception_type,
                note=f"Test istisnası {j+1}"
            )
    print(f"Uzmanlar için takvim ve istisnai durumlar başarıyla oluşturuldu. Oluşturulan: {created_count}, Atlanan: {skipped_count}")


def run():
    create_availability_and_exceptions()