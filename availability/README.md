# Test Feed Scripti Kullanımı

Test verisi oluşturmak için `scripts/feed_availability.py` scriptini kullanabilirsiniz. Bu script, ilk 10 uzmana 3 adet takvim ve 5 adet istisnai durum (gelecek 3 aya yayılmış şekilde) ekler.

Kullanım:

```bash
python manage.py runscript feed_availability
```

Scripti çalıştırmadan önce veritabanınızda en az 10 uzman (ExpertProfile) olduğundan emin olun.

Script başarıyla çalıştığında, uzmanlar için takvim ve istisnai durumlar oluşturulmuş olur.
# Availability Management System

Bu modül, uzmanların müsaitlik durumlarını yönetmek için tasarlanmıştır.

## Özellikler

### 1. Weekly Availability (Haftalık Müsaitlik)
- Uzmanlar haftanın belirli günlerinde çalışma saatlerini tanımlayabilir.
- Her gün için farklı saat aralıkları ve hizmetler belirlenebilir.
- Slot süresi ve kapasite ayarlanabilir.
- Zaman dilimi desteği.

### 2. Availability Exceptions (Müsaitlik İstisnaları)
- **Cancel**: Belirli günleri iptal etme.
- **Add**: Ekstra çalışma günleri ekleme.
- Tarih bazlı özel durumlar.
- Not ekleme imkanı.

### 3. Takvim Görünümü
- Uzmanlar, kendi haftalık programlarını ve istisnalarını birleştirerek aylık veya yıllık takvim görünümünde görüntüleyebilir.

---

## Kullanım Akışı

### 1. Haftalık Program Oluşturma
Uzman, haftalık programını oluşturmak için `POST /appointments/availability/weekly/` endpoint'ini kullanır. Bu program, tüm yıl boyunca tekrar eden bir yapı olarak kabul edilir.

### 2. Haftalık Programı Görüntüleme
Uzman, mevcut haftalık programını görmek için `GET /appointments/availability/weekly/` endpoint'ini kullanır. Dönen veriler, haftalık görünümde işlenir.

### 3. Aylık Görünüm ve İstisnalar
- Haftalık program, aylık görünümde tekrar eden bir yapı olarak gösterilir.
- İstisnalar (cancel veya add), haftalık programın üzerine işlenir.
- İstisnalar için `GET /appointments/availability/exceptions/` endpoint'i kullanılır.

### 4. Takvim Görünümü
Uzman, kendi takvim görünümünü görmek için `GET /appointments/availability/expert/{expert_id}/calendar/` endpoint'ini kullanabilir. Bu endpoint, haftalık program ve istisnaları birleştirerek döner.

---

## Güvenlik

- Sadece `expert` rolüne sahip kullanıcılar müsaitlik tanımlayabilir.
- Her uzman sadece kendi müsaitliklerini yönetebilir.
- GET istekleri için kimlik doğrulama gerekli.
- POST/PUT/DELETE için expert rolü zorunlu.

---

## Validasyon Kuralları

- Başlangıç saati bitiş saatinden önce olmalı.
- Add tipinde istisnalar için start_time ve end_time zorunlu.
- Tarih formatı: YYYY-MM-DD.
- Saat formatı: HH:MM:SS.

---

## Model İlişkileri

- `WeeklyAvailability` → `ExpertProfile` (ForeignKey).
- `WeeklyAvailability` → `Service` (ForeignKey, optional).
- `AvailabilityException` → `ExpertProfile` (ForeignKey).
- `AvailabilityException` → `Service` (ForeignKey, optional).
