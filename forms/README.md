# Forms App

Bu Django app'i, kullanıcıların farklı tiplerde sorular içeren formları doldurmasını sağlar.

## Özellikler

- **Farklı Soru Tipleri:**
  - Açık uçlu (Text) sorular
  - Test (A/B/C/D) soruları
  - Çok seçimli sorular
- **Authentication Koruması:** Sadece giriş yapmış kullanıcılar formlara erişebilir
- **Form Yönetimi:** Admin panelinden form ve soru oluşturma/düzenleme
- **Cevap Takibi:** Kullanıcıların form cevaplarını görüntüleme

## Modeller

### Form
- Form başlığı ve açıklaması
- Aktif/pasif durumu
- Oluşturulma ve güncellenme tarihleri

### Question
- Soru metni ve tipi
- Sıralama ve zorunluluk durumu
- Form ile ilişki

### QuestionOption
- Test ve çok seçimli sorular için seçenekler
- Sıralama

### FormResponse
- Kullanıcının form doldurma kaydı
- Form ve kullanıcı ile ilişki

### Answer
- Kullanıcının sorulara verdiği cevaplar
- Metin cevabı veya seçilen seçenekler

## API Endpoints

### GET `/api/v1/forms/`
- Aktif formların listesini getirir
- Authentication gerekli

### GET `/api/v1/forms/{form_id}/`
- Belirli bir formun detaylarını ve sorularını getirir
- Authentication gerekli
- `has_responded` field'ı ile kullanıcının formu daha önce doldurup doldurmadığı bilgisi

### POST `/api/v1/forms/submit/`
- Form cevaplarını gönderir
- Authentication gerekli
- Bir kullanıcı bir formu sadece bir kez doldurabilir

### GET `/api/v1/forms/my-responses/`
- Kullanıcının doldurduğu formları getirir
- Authentication gerekli

### GET `/api/v1/forms/responses/{response_id}/`
- Belirli bir form cevabının detaylarını getirir
- Authentication gerekli
- Sadece kendi cevaplarını görüntüleyebilir

## Kullanım Örnekleri

### Form Gönderimi

```json
POST /api/v1/forms/submit/
{
    "form_id": 1,
    "answers": [
        {
            "question_id": 1,
            "text_answer": "Baş ağrısı ve mide bulantısı yaşıyorum"
        },
        {
            "question_id": 2,
            "selected_option_ids": [3]
        },
        {
            "question_id": 3,
            "selected_option_ids": [6, 9, 10]
        }
    ]
}
```

### Form Detayı

```json
GET /api/v1/forms/1/
{
    "id": 1,
    "title": "Hasta Değerlendirme Formu",
    "description": "Hastaların genel durumunu değerlendirmek için kullanılan form",
    "is_active": true,
    "created_at": "2025-01-15T10:00:00Z",
    "has_responded": false,
    "questions": [
        {
            "id": 1,
            "question_text": "Hangi şikayetlerle başvurdunuz? Lütfen detaylı olarak açıklayın.",
            "question_type": "text",
            "order": 1,
            "is_required": true,
            "options": []
        },
        {
            "id": 2,
            "question_text": "Ağrı şiddetinizi nasıl değerlendirirsiniz?",
            "question_type": "test",
            "order": 2,
            "is_required": true,
            "options": [
                {"id": 1, "option_text": "Hiç ağrım yok", "order": 1},
                {"id": 2, "option_text": "Hafif ağrı", "order": 2},
                {"id": 3, "option_text": "Orta şiddette ağrı", "order": 3},
                {"id": 4, "option_text": "Şiddetli ağrı", "order": 4},
                {"id": 5, "option_text": "Dayanılmaz ağrı", "order": 5}
            ]
        }
    ]
}
```

## Kurulum

1. App'i `INSTALLED_APPS`'e ekleyin
2. Migrations'ları çalıştırın: `python manage.py makemigrations forms`
3. Veritabanını güncelleyin: `python manage.py migrate`
4. Örnek verileri oluşturun: `python manage.py create_sample_forms`

## Admin Panel

Admin panelinden form, soru ve seçenekleri yönetebilirsiniz:
- Form oluşturma/düzenleme
- Soru ekleme/düzenleme
- Seçenek ekleme/düzenleme
- Form cevaplarını görüntüleme

## Güvenlik

- Tüm endpoint'ler authentication gerektirir
- Kullanıcılar sadece kendi form cevaplarını görüntüleyebilir
- Bir kullanıcı bir formu sadece bir kez doldurabilir
- Form validasyonu backend'de yapılır
