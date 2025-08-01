# Zoom Entegrasyonu

Bu modül, Lunova platformunda Zoom video konferans entegrasyonunu sağlar. Randevu oluşturma ve Zoom toplantı yönetimi için API endpoint'leri sunar.

## 🚀 Özellikler

- **Otomatik Zoom Toplantı Oluşturma**: Randevu oluşturulduğunda otomatik olarak Zoom toplantısı oluşturulur
- **Toplantı Yönetimi**: Toplantı bilgilerini alma, güncelleme ve silme
- **Randevu Sistemi**: Uzman-danışan randevu yönetimi
- **Güvenlik**: Kimlik doğrulama ve yetkilendirme kontrolleri

## 📋 API Endpoint'leri

### 1. Zoom Toplantı Oluşturma
```
POST /api/v1/zoom/meetings/ - Zoom toplantısı oluştur
```

**Açıklama**: Yeni bir Zoom toplantısı oluşturur.

**İstek Gövdesi**:
toplantı başlığını güzel göndermek lazım
```json
{
    "topic": "Toplantı Başlığı",
    "start_time": "2024-01-15T10:00:00Z",
    "duration": 45
}
```

**Yanıt**:
```json
{
    "success": true,
    "meeting_id": "123456789",
    "start_url": "https://zoom.us/s/123456789?zak=...",
    "join_url": "https://zoom.us/j/123456789",
    "topic": "Toplantı Başlığı",
    "start_time": "2024-01-15T10:00:00Z",
    "duration": 45,
    "password": "123456",
    "host_email": "host@example.com"
}
```

## 🔐 Kimlik Doğrulama

Tüm endpoint'ler kimlik doğrulama gerektirir. JWT token kullanılır.

## 🛡️ Yetkilendirme

- **Zoom Toplantı Oluşturma**: Sadece uzman rolündeki kullanıcılar
- **Randevu Oluşturma**: Sadece uzman rolündeki kullanıcılar
- **Randevu Görüntüleme**: Sadece randevuya dahil olan kullanıcılar (uzman veya danışan)
- **Randevu Onaylama**: Sadece randevunun uzmanı
- **Randevu Güncelleme/Silme**: Sadece randevuya dahil olan kullanıcılar

## ⚙️ Çevre Değişkenleri

`.env` dosyasında aşağıdaki Zoom API bilgileri bulunmalıdır:

```env
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
ZOOM_ACCOUNT_ID=your_zoom_account_id
```

## 📁 Dosya Yapısı

```
zoom/                      # Bağımsız Zoom Django App
├── __init__.py
├── apps.py               # Django app konfigürasyonu
├── models.py             # Appointment modeli
├── services.py           # Zoom API fonksiyonları (create_meeting, get_token)
├── serializers.py        # API serializer'ları
├── views.py              # API view'ları
├── urls.py               # API URL yapılandırması
├── settings.py           # Zoom ayarları
├── migrations/           # Veritabanı migration'ları
└── README.md            # Bu dosya
```

## 🔧 Kurulum

1. Zoom API bilgilerini `.env` dosyasına ekleyin
2. Django migration'larını çalıştırın:
   ```bash
   python manage.py makemigrations zoom
   python manage.py migrate
   ```
3. Sunucuyu başlatın:
   ```bash
   python manage.py runserver
   ```

## 📝 Notlar

- Zoom toplantıları otomatik olarak 45 dakika süreyle oluşturulur
- Toplantılar "Europe/Istanbul" saat diliminde oluşturulur
- Bekleme odası aktif, ev sahibi olmadan katılım kapalı
- Randevu oluşturulduğunda otomatik olarak Zoom toplantısı da oluşturulur 