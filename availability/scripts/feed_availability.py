# availability/scripts/seed_availability.py
"""
Bu script, veritabanındaki ilk 10 uzman (Expert) için çeşitli haftalık müsaitlik (WeeklyAvailability) ve istisnai durum (AvailabilityException) kayıtları oluşturur.
Test ortamında kullanılmak üzere tasarlanmıştır.
"""

import random
from datetime import datetime, timedelta, time
from availability.models import WeeklyAvailability, AvailabilityException
from accounts.models import ExpertProfile, Service


def create_availability_and_exceptions():
    """
    Veritabanına test verisi ekler.
    Bu fonksiyonu 'python manage.py runscript availability.scripts.feed_availability' ile çalıştırın.
    """
    # İlk 10 uzmanı al
    experts = ExpertProfile.objects.all()[:10]
    # İlk 3 servisi al (eğer varsa)
    services = Service.objects.all()[:3]
    now = datetime.now()
    
    if not experts:
        print("Uyarı: Hiç uzman bulunamadı. Lütfen önce uzman ekleyin.")
        return

    for expert in experts:
        # Her uzman için 3 farklı gün ve saat aralığında haftalık müsaitlik oluştur
        for i in range(3):
            # Haftanın gününü rastgele seç
            day_of_week = random.randint(0, 6)
            start_time = time(hour=random.randint(8, 15), minute=0)
            end_time = (datetime.combine(now.date(), start_time) + timedelta(hours=2)).time()
            
            # Servis nesnesini al veya None olarak ayarla
            service = random.choice(services) if services else None
            
            WeeklyAvailability.objects.create(
                expert=expert,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                service=service,
                is_active=True
            )
        
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
    print("Uzmanlar için takvim ve istisnai durumlar başarıyla oluşturuldu.")


def run():
    create_availability_and_exceptions()