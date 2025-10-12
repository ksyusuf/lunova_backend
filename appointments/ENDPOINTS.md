# Appointments API Endpoints

Bu dokümanda Appointments API'sinin tüm endpoint'leri kısaca açıklanmıştır.

## Genel Bilgiler

- **Base URL**: `/api/v1/appointments/`
- **Authentication**: JWT Token (Bearer)
- **Content-Type**: `application/json`

## Endpoint Listesi

### 1. Randevu Listesi
```
GET /api/v1/appointments/
```
**Açıklama**: Kullanıcının randevularını listeler
**Query Params**:
- `mine` (boolean): Sadece kendi randevularımı (true/false)
- `status` (string): Duruma göre filtrele
**Yetki**: Authenticated users

### 2. Uzman Randevu Oluşturma
```
POST /api/v1/appointments/expert/create/
```
**Açıklama**: Uzman yeni randevu oluşturur (Zoom otomatik)
**Yetki**: Experts only

### 3. Danışan Randevu Talebi
```
POST /api/v1/appointments/client/request/
```
**Açıklama**: Danışan randevu talebi gönderir
**Yetki**: Clients only

### 4. Randevu Detayı
```
GET /api/v1/appointments/{id}/
```
**Açıklama**: Randevu detaylarını getirir
**Yetki**: Appointment participants

### 5. Randevu Tam Güncelleme
```
PUT /api/v1/appointments/{id}/
```
**Açıklama**: Randevunun tüm alanlarını günceller
**Yetki**: Appointment participants

### 6. Randevu Kısmi Güncelleme
```
PATCH /api/v1/appointments/{id}/
```
**Açıklama**: Randevunun belirli alanlarını günceller
**Yetki**: Appointment participants

### 7. Randevu Durum Güncelleme (RESTful)
```
PATCH /api/v1/appointments/{id}/status/
```
**Açıklama**: Sadece randevu durumunu günceller
**Request Body**: `{"status": "confirmed"}`
**Geçerli Durumlar**: pending, waiting_approval, confirmed, cancel_requested, cancelled, completed
**Yetki**: Role-based (experts for confirm/cancel/complete, clients for cancel_request)

### 8. Randevu Silme (Soft Delete)
```
DELETE /api/v1/appointments/{id}/
```
**Açıklama**: Randevuyu soft delete yapar
**Yetki**: Appointment participants

### 9. Zoom Meeting Bilgileri
```
GET /api/v1/appointments/{id}/meeting-info/
```
**Açıklama**: Zoom meeting bilgilerini getirir
**Yetki**: Appointment participants

## Durum Geçiş Kuralları

- `pending` → `confirmed`, `cancelled`
- `waiting_approval` → `confirmed`, `cancelled`
- `confirmed` → `cancel_requested`, `completed`
- `cancel_requested` → `cancelled`, `confirmed`
- `cancelled`, `completed`: Son durumlar

## Yetki Kuralları

- **Admin**: Tüm randevuları görebilir
- **Expert**: Kendi randevularını yönetebilir, onay verebilir
- **Client**: Kendi randevularını yönetebilir, iptal talebi gönderebilir

## Hata Kodları

- `400`: Geçersiz istek veya durum geçişi
- `401`: Kimlik doğrulama hatası
- `403`: Yetki hatası
- `404`: Randevu bulunamadı