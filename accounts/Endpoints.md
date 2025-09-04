# Accounts API Endpoints

Bu dokümantasyon, Lunova Backend Accounts uygulamasının API endpoint'lerini açıklar.

## Base URL
```
http://127.0.0.1:8000/api/v1/accounts/
```

## Endpoints

### 1. Expert Registration
**POST** `/register/expert/`

Uzman kullanıcı kaydı için kullanılır.

**Request Body:**
```json
{
  "first_name": "Yusuf",
  "last_name": "Kahraman",
  "email": "uzman@example.com",
  "password": "sifre123",
  "password2": "sifre123",
  "phone_number": "05318849781",
  "id_number": "15111111311",
  "country": "TR",
  "national_id": "",
  "university": "İstanbul Üniversitesi",
  "about": "Uzman psikolog",
  "degree_file": null,
  "gender_id": 1,
  "birth_date": "1990-01-20"
}
```

**Required Fields:**
- `first_name`, `last_name`, `email`, `password`, `password2`
- `phone_number`, `id_number` (TR için), `university`

**Response:**
```json
{
  "id": 1,
  "username": "uzman@example.com",
  "email": "uzman@example.com",
  "first_name": "Yusuf",
  "last_name": "Kahraman",
  "role": "expert"
}
```

### 2. Client Registration
**POST** `/register/client/`

Danışan kullanıcı kaydı için kullanılır.

**Request Body:**
```json
{
  "first_name": "Ahmet",
  "last_name": "Yılmaz",
  "email": "danisan@example.com",
  "password": "sifre123",
  "password2": "sifre123",
  "phone_number": "05321234567",
  "id_number": "12345678901",
  "country": "TR",
  "national_id": "",
  "birth_date": "1995-04-12",
  "gender_id": 2,
  "support_goal": "Bağımlılık tedavisi",
  "received_service_before": false
}
```

**Required Fields:**
- `first_name`, `last_name`, `email`, `password`, `password2`
- `phone_number`, `id_number` (TR için)

**Response:**
```json
{
  "id": 2,
  "username": "danisan@example.com",
  "email": "danisan@example.com",
  "first_name": "Ahmet",
  "last_name": "Yılmaz",
  "role": "client"
}
```

### 3. Admin Registration
**POST** `/register/admin/`

Admin kullanıcı kaydı için kullanılır.

**Request Body:**
```json
{
  "first_name": "Admin",
  "last_name": "User",
  "email": "admin@lunova.com",
  "password": "admin123",
  "password2": "admin123",
  "phone_number": "05329998877",
  "id_number": "98765432109",
  "country": "TR",
  "national_id": ""
}
```

**Required Fields:**
- `first_name`, `last_name`, `email`, `password`, `password2`
- `phone_number`, `id_number` (TR için)

**Response:**
```json
{
  "id": 3,
  "username": "admin@lunova.com",
  "email": "admin@lunova.com",
  "first_name": "Admin",
  "last_name": "User",
  "role": "admin"
}
```

### 4. Login
**POST** `/login/`

Kullanıcı girişi için kullanılır.

**Request Body:**
```json
{
  "email": "uzman@example.com",
  "password": "sifre123"
}
```

**Response:**
```json
{
  "refresh": "refresh_token_here",
  "access": "access_token_here",
  "email": "uzman@example.com",
  "role": "expert"
}
```

### 5. Logout
**POST** `/logout/`

Kullanıcı çıkışı için kullanılır. Authentication gerekir.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "detail": "Başarıyla çıkış yapıldı."
}
```

### 6. Me
**GET** `/me/`

Mevcut kullanıcı bilgilerini getirir. Authentication gerekir.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "username": "uzman@example.com",
  "email": "uzman@example.com",
  "role": "expert",
  "first_name": "Yusuf",
  "last_name": "Kahraman"
}
```

## Önemli Notlar

1. **Role Field**: Artık register request'lerinde `role` field'ı gönderilmemelidir. Role otomatik olarak endpoint'e göre belirlenir.

2. **Validation**: Her endpoint kendi validation kurallarını uygular:
   - Expert: `university` field'ı zorunludur
   - Client: `birth_date`, `gender_id`, `support_goal` gibi ek field'lar mevcuttur
   - Admin: Sadece temel bilgiler gerekir

3. **TC Kimlik**: Türkiye için `id_number` (11 haneli) zorunludur.

4. **International Users**: Türkiye dışı kullanıcılar için `national_id` field'ı kullanılır.

5. **Profile Creation**: Her kayıt işleminde ilgili profile (ExpertProfile, ClientProfile, AdminProfile) otomatik olarak oluşturulur.

6. **Gender (Destek Tablosu)**: `gender` destekleyici bir tablodur. İsteklerde `gender_id` gönderilmelidir (opsiyonel). Yanıtlarda `gender` FK olarak döner.
