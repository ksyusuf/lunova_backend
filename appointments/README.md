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

Detaylı endpoint dokümantasyonu için: [ENDPOINTS.md](ENDPOINTS.md)

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
2. POST /api/v1/appointments/expert/create/ ile randevu oluşturur
3. Sistem otomatik Zoom meeting oluşturur
4. Randevu 'pending' durumunda oluşturulur
5. Uzman PATCH /api/v1/appointments/{id}/status/ ile durumu 'confirmed' yapar

### Senaryo 2: Danışan Randevu Talebi
1. Danışan giriş yapar ve JWT token alır
2. POST /api/v1/appointments/client/request/ ile randevu talebi gönderir
3. Sistem randevuyu 'waiting_approval' durumunda oluşturur
4. Uzman PATCH /api/v1/appointments/{id}/status/ ile durumu 'confirmed' yapar
5. Sistem Zoom meeting oluşturur ve durum 'confirmed' olur

### Senaryo 3: Randevu İptal Süreci
1. Danışan onaylanmış randevu için PATCH /api/v1/appointments/{id}/status/ ile 'cancel_requested' durumuna getirir
2. Randevu durumu 'cancel_requested' olur
3. Uzman PATCH /api/v1/appointments/{id}/status/ ile 'cancelled' (onay) veya 'confirmed' (red) yapar

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
