# Appointments API Dokümantasyonu

Bu API, uzmanlar ve müşteriler arasında randevu yönetimi için kullanılır. Otomatik Zoom entegrasyonu ile online görüşme desteği sağlar.

## API Yapısı

### Model Yapısı
- **Expert**: Randevuyu veren uzman kullanıcı
- **Client**: Randevuyu alan müşteri kullanıcı
- **Date/Time**: Randevu tarihi ve saati
- **Duration**: Randevu süresi (varsayılan 45 dakika)
- **Status**: Randevu durumu (6 farklı durum)
- **Zoom Integration**: Otomatik Zoom meeting oluşturma

### Yetkilendirme (Authentication)

API'ye erişim için JWT token gereklidir. Token'ı Authorization header'ında gönderin:

```
Authorization: Bearer <your-jwt-token>
```

**Önemli**: Authorization header formatı şu şekilde olmalıdır:
- Doğru: `Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`
- Yanlış: `Authorization: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...` (Bearer eksik)
- Yanlış: `Authorization: Bearer` (Token eksik)

### İzin Yapısı (Permissions)

1. **IsExpertOrClientForCreatePermission**:
   - GET istekleri: Tüm kimlik doğrulanmış kullanıcılar
   - POST: Uzmanlar ve danışanlar
   - PUT/DELETE: Sadece uzmanlar

2. **IsAppointmentParticipantPermission**:
   - Randevuya dahil olan kullanıcılar (expert veya client)

3. **Manuel Permission Kontrolü**:
   - Özel endpoint'lerde manuel olarak kullanıcı yetkisi kontrol edilir
   - Sadece ilgili uzman veya danışan işlem yapabilir

## Durum Kodları (Status)

- **pending**: Beklemede - Uzman tarafından oluşturuldu, onay bekliyor
- **waiting_approval**: Onay Bekliyor - Danışan tarafından oluşturuldu, uzman onayı bekliyor
- **confirmed**: Onaylandı - Randevu onaylanmış ve Zoom meeting oluşturulmuş
- **cancel_requested**: İptal Talep Edildi - Danışan iptal talebi göndermiş, uzman onayı bekliyor
- **cancelled**: İptal Edildi - Randevu iptal edilmiş
- **completed**: Tamamlandı - Randevu gerçekleştirilmiş

## API Endpoints

### 1. Randevuları Listele
```
GET /api/v1/appointments/
```

**Yetki**: Kimlik doğrulanmış kullanıcılar
**Açıklama**: Kullanıcının dahil olduğu tüm randevuları listeler (sadece listeleme)

**Örnek İstek:**
```bash
curl -X GET "http://localhost:8000/api/v1/appointments/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

**Örnek Yanıt:**
```json
[
  {
    "id": 1,
    "expert": 2,
    "client": 3,
    "expert_name": "Dr. Ahmet Yılmaz",
    "client_name": "Ayşe Demir",
    "date": "2024-01-15",
    "time": "14:30:00",
    "duration": 45,
    "is_confirmed": true,
    "notes": "İlk görüşme",
    "status": "confirmed",
    "zoom_start_url": "https://zoom.us/s/123456789?zak=...",
    "zoom_join_url": "https://zoom.us/j/123456789",
    "zoom_meeting_id": "123456789",
    "created_at": "2024-01-10T10:00:00Z",
    "updated_at": "2024-01-12T15:30:00Z"
  }
]
```

### 2. Uzman Randevu Oluşturma
```
POST /api/v1/appointments/expert/create/
```

**Yetki**: Sadece uzmanlar
**Açıklama**: Uzman yeni randevu oluşturur ve otomatik Zoom meeting oluşturur
NOT: istek gövdesinde farklı uzmana da randevu oluşturuyor. yani arkada token ve uzman id eşelştirme kontrolü yok. düzeltilebilir.

**Örnek İstek:**
```bash
curl -X POST "http://localhost:8000/api/v1/appointments/expert/create/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "expert": 2,
    "client": 3,
    "date": "2024-01-20",
    "time": "15:00:00",
    "duration": 60,
    "notes": "Takip görüşmesi"
  }'
```

**Örnek Yanıt:**
```json
{
  "id": 2,
  "expert": 2,
  "client": 3,
  "expert_name": "Dr. Ahmet Yılmaz",
  "client_name": "Ayşe Demir",
  "date": "2024-01-20",
  "time": "15:00:00",
  "duration": 60,
  "is_confirmed": false,
  "notes": "Takip görüşmesi",
  "status": "pending",
  "zoom_start_url": "https://zoom.us/s/987654321?zak=...",
  "zoom_join_url": "https://zoom.us/j/987654321",
  "zoom_meeting_id": "987654321",
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

### 3. Danışan Randevu Talebi
```
POST /api/v1/appointments/client/request/
```

**Yetki**: Sadece danışanlar
**Açıklama**: Danışan randevu talebi oluşturur, uzman onayı bekler (Zoom meeting henüz oluşturulmaz)

**Örnek İstek:**
```bash
curl -X POST "http://localhost:8000/api/v1/appointments/client/request/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "expert": 2,
    "date": "2024-01-25",
    "time": "10:00:00",
    "duration": 45,
    "notes": "İlk danışmanlık talebi"
  }'
```

**Not**: Danışan randevu oluştururken `client` alanı gönderilmez, sistem otomatik olarak giriş yapmış kullanıcıyı client olarak atar.

**Örnek Yanıt:**
```json
{
  "id": 3,
  "expert": 2,
  "expert_name": "Dr. Ahmet Yılmaz",
  "client_name": "Mehmet Kaya",
  "date": "2024-01-25",
  "time": "10:00:00",
  "duration": 45,
  "notes": "İlk danışmanlık talebi",
  "status": "waiting_approval",
  "created_at": "2024-01-20T09:00:00Z",
  "updated_at": "2024-01-20T09:00:00Z"
}
```

### 4. Randevu Detayı
```
GET /api/v1/appointments/<id>/
```

**Yetki**: Randevuya dahil olan kullanıcılar
**Açıklama**: Belirli bir randevunun detaylarını getirir

**Örnek İstek:**
```bash
curl -X GET "http://localhost:8000/api/v1/appointments/1/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 5. Randevu Güncelle
```
PUT /api/v1/appointments/<id>/
```

**Yetki**: Randevuya dahil olan kullanıcılar
**Açıklama**: 2 tip güncelleme vardır, put (tam) ve patch (kısmi) güncelleme yapar.

**Örnek Tam (Put) İstek:**
```bash
curl -X PUT "http://localhost:8000/api/v1/appointments/5/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "expert": 5,
    "client": 12,
    "date": "2025-08-20",
    "time": "14:30:00",
    "duration": 90,
    "notes": "5 id li randevu TAM Güncellenmiş notlar"
  }'
```

**Örnek Kısmi (Patch) İstek:**
```bash
curl -X PUT "http://localhost:8000/api/v1/appointments/19/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
      "notes": "19 id li randevu KISMİ Güncellenmiş notlar",
      "duration": 45
    }'
```

### 6. Randevu Sil
```
DELETE /api/v1/appointments/<id>/
```

**Yetki**: Randevuya dahil olan kullanıcılar
**Açıklama**: Randevuyu siler

**Örnek İstek:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/appointments/21/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 7. Kullanıcı Randevuları
```
GET /api/v1/appointments/user/
```

**Yetki**: Kimlik doğrulanmış kullanıcılar
**Açıklama**: Mevcut kullanıcının tüm randevularını listeler

**Örnek İstek:**
```bash
curl -X GET "http://localhost:8000/api/v1/appointments/user/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 8. Randevu Onayla (Uzman Randevusu)
```
POST /api/v1/appointments/<id>/confirm/
```

**Yetki**: Sadece randevunun uzmanı
**Açıklama**: Uzman tarafından oluşturulan randevuyu onaylar

**Örnek İstek:**
```bash
curl -X POST "http://localhost:8000/api/v1/appointments/1/confirm/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 9. Danışan Randevu Talebini Onayla
```
POST /api/v1/appointments/<id>/approve/
```

**Yetki**: Sadece randevunun uzmanı
**Açıklama**: Danışan tarafından oluşturulan randevu talebini onaylar ve Zoom meeting oluşturur

**Örnek İstek:**
```bash
curl -X POST "http://localhost:8000/api/v1/appointments/3/approve/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

**Örnek Yanıt:**
```json
{
  "id": 3,
  "expert": 2,
  "client": 4,
  "expert_name": "Dr. Ahmet Yılmaz",
  "client_name": "Mehmet Kaya",
  "date": "2024-01-25",
  "time": "10:00:00",
  "duration": 45,
  "is_confirmed": true,
  "notes": "İlk danışmanlık talebi",
  "status": "confirmed",
  "zoom_start_url": "https://zoom.us/s/555666777?zak=...",
  "zoom_join_url": "https://zoom.us/j/555666777",
  "zoom_meeting_id": "555666777",
  "created_at": "2024-01-20T09:00:00Z",
  "updated_at": "2024-01-20T11:30:00Z"
}
```

### 10. Randevu İptal Talebi Gönder
```
POST /api/v1/appointments/<id>/cancel-request/
```

**Yetki**: Sadece randevunun danışanı
**Açıklama**: Onaylanmış randevu için iptal talebi gönderir

**Örnek İstek:**
```bash
curl -X POST "http://localhost:8000/api/v1/appointments/1/cancel-request/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

**Örnek Yanıt:**
```json
{
  "id": 1,
  "status": "cancel_requested",
  "message": "İptal talebi gönderildi, uzman onayı bekleniyor."
}
```

### 11. İptal Talebini Onayla/Reddet
```
POST /api/v1/appointments/<id>/cancel-confirm/
```

**Yetki**: Sadece randevunun uzmanı
**Açıklama**: Danışanın iptal talebini onaylar veya reddeder

**Örnek İstek (Onaylama):**
```bash
curl -X POST "http://localhost:8000/api/v1/appointments/1/cancel-confirm/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "confirm": true
  }'
```

**Örnek Yanıt (Onaylama):**
```json
{
  "id": 1,
  "status": "cancelled",
  "message": "Randevu iptal edildi"
}
```

**Örnek İstek (Reddetme):**
```bash
curl -X POST "http://localhost:8000/api/v1/appointments/1/cancel-confirm/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "confirm": false
  }'
```

**Örnek Yanıt (Reddetme):**
```json
{
  "id": 1,
  "status": "confirmed",
  "message": "İptal talebi reddedildi"
}
```

**Örnek İptal Edilememe Yanıt:**
```json
{
    "error": "Bu randevu iptal talebi bekleyen durumda değil"
}
```

### 12. Zoom Meeting Bilgileri
```
GET /api/v1/appointments/<id>/meeting-info/
```

**Yetki**: Randevuya dahil olan kullanıcılar
**Açıklama**: Randevunun Zoom meeting bilgilerini getirir

**Örnek İstek:**
```bash
curl -X GET "http://localhost:8000/api/v1/appointments/1/meeting-info/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

**Örnek Yanıt:**
```json
{
  "appointment_id": 1,
  "meeting_id": "123456789",
  "start_url": "https://zoom.us/s/123456789?zak=...",
  "join_url": "https://zoom.us/j/123456789",
  "topic": "Danışmanlık: Ayşe Demir - Uzman Dr. Ahmet Yılmaz",
  "date": "2024-01-15",
  "time": "14:30:00",
  "duration": 45,
  "is_confirmed": true,
  "status": "confirmed"
}
```
**Örnek Hata:**
```json
{
    "error": "Bu randevuyu görüntüleme yetkiniz yok"
}
```

## Hata Kodları

### 400 Bad Request
```json
{
  "error": "Bu tarih ve saatte uzmanın başka bir randevusu bulunmaktadır."
}
```

```json
{
  "error": "Sadece onaylanmış randevular için iptal talebi gönderilebilir"
}
```

```json
{
  "error": "Bu randevu onay bekleyen durumda değil"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "Bu randevuyu görüntüleme yetkiniz yok"
}
```

```json
{
  "error": "Bu randevuyu onaylama yetkiniz yok"
}
```

```json
{
  "error": "Bu randevu için iptal talebi gönderme yetkiniz yok"
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Zoom Entegrasyonu

### Zoom Meeting Oluşturma Kuralları:
- **Uzman randevusu**: Oluşturulduğunda hemen Zoom meeting oluşturulur
- **Danışan talebi**: Sadece uzman onayladığında Zoom meeting oluşturulur
- **İptal durumu**: Zoom meeting bilgileri korunur ama erişim engellenir

### Zoom URL'leri:
- **start_url**: Uzmanın meeting'i başlatması için kullanacağı URL
- **join_url**: Katılımcıların meeting'e katılması için kullanacağı URL
- **meeting_id**: Zoom meeting ID'si

## Güvenlik Notları

1. Tüm API çağrıları JWT token ile kimlik doğrulaması gerektirir
2. Uzmanlar ve danışanlar randevu oluşturabilir (farklı akışlar)
3. Kullanıcılar sadece dahil oldukları randevuları görebilir
4. Randevu onaylama yetkisi sadece uzmanlarda
5. İptal talebi sadece danışanlar gönderebilir
6. İptal onayı sadece uzmanlar verebilir
7. Zoom URL'leri hassas bilgilerdir, güvenli şekilde saklanmalıdır

## Örnek Kullanım Senaryoları

### Senaryo 1: Uzman Randevu Oluşturma
1. Uzman giriş yapar ve JWT token alır
2. POST /api/v1/appointments/ ile randevu oluşturur
3. Sistem otomatik Zoom meeting oluşturur
4. Randevu 'pending' durumunda oluşturulur
5. Uzman POST /appointments/{id}/confirm/ ile onaylar

### Senaryo 2: Danışan Randevu Talebi
1. Danışan giriş yapar ve JWT token alır
2. POST /api/v1/appointments/ ile randevu talebi gönderir
3. Sistem randevuyu 'waiting_approval' durumunda oluşturur
4. Uzman POST /appointments/{id}/approve/ ile onaylar
5. Sistem Zoom meeting oluşturur ve durum 'confirmed' olur

### Senaryo 3: Randevu İptal Süreci
1. Danışan onaylanmış randevu için POST /appointments/{id}/cancel-request/ ile iptal talebi gönderir
2. Randevu durumu 'cancel_requested' olur
3. Uzman POST /appointments/{id}/cancel-confirm/ ile talebi değerlendirir
4. Onaylanırsa 'cancelled', reddedilirse 'confirmed' durumuna döner

### Senaryo 4: Meeting'e Katılma
1. Kullanıcı GET /api/v1/appointments/{id}/meeting-info/ ile Zoom bilgilerini alır
2. Uygun URL ile Zoom meeting'e katılır

## Durum Geçiş Diyagramı

```
Uzman Randevusu:
pending → confirmed → completed
pending → cancelled

Danışan Talebi:
waiting_approval → confirmed → completed
waiting_approval → cancelled

İptal Süreci:
confirmed → cancel_requested → cancelled
confirmed → cancel_requested → confirmed (reddedilirse)
```

## Validasyon Kuralları

1. **Tarih/Saat Kontrolü**: Aynı uzman için aynı tarih/saatte çakışan randevu olamaz
2. **Rol Kontrolü**: Sadece 'expert' ve 'client' rollü kullanıcılar randevu oluşturabilir
3. **Durum Kontrolü**: Sadece uygun durumlardaki randevular için işlem yapılabilir
4. **Yetki Kontrolü**: Kullanıcılar sadece kendi randevularında işlem yapabilir
