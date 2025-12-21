# Forms App

Bu Django app'i, kullanıcıların farklı tiplerde sorular içeren formları doldurmasını sağlar. Madde kullanım tarama, bağımlılık değerlendirmesi ve genel sağlık formları gibi özelleşmiş formları destekler.

## Model Yapısı

### Form Modeli
Form ana modeli - tüm formların temel özelliklerini içerir:
- **title**: Form başlığı
- **description**: Form açıklaması
- **is_active**: Form aktiflik durumu
- **stage**: Form aşama numarası (adım adım formlarda kullanılır)
- **instructions**: Form doldurma talimatları
- **disclaimer**: Etik hatırlatma metni
- **max_score**: Maksimum puan (skorlama sistemi için)
- **min_score**: Minimum puan
- **scoring_type**: Puanlama tipi (none, binary, scale, weighted, custom)

### Question Modeli
Soru modeli - form içindeki her soru:
- **form**: İlişkili form
- **question_text**: Soru metni
- **question_type**: Soru tipi
- **order**: Soru sırası
- **is_required**: Zorunlu soru olup olmadığı
- **score_weight**: Puan ağırlığı
- **min_scale_value**: Ölçek soruları için minimum değer
- **max_scale_value**: Ölçek soruları için maksimum değer
- **scale_labels**: Ölçek etiketleri (JSON format)

### QuestionOption Modeli
Soru seçenekleri - çoktan seçmeli sorular için:
- **question**: İlişkili soru
- **option_text**: Seçenek metni
- **order**: Seçenek sırası
- **score_value**: Seçenek puan değeri
- **is_correct**: Doğru cevap olup olmadığı

### FormResponse Modeli
Form cevapları - kullanıcıların form doldurma kayıtları:
- **form**: İlişkili form
- **user**: Kullanıcı
- **submitted_at**: Gönderilme tarihi
- **total_score**: Toplam puan (otomatik hesaplanır)
- **risk_level**: Risk seviyesi (otomatik hesaplanır)
- **percentage_score**: Yüzde puan
- **interpretation**: Yorum metni
- **recommendations**: Öneriler

### Answer Modeli
Cevap modeli - kullanıcıların sorulara verdiği cevaplar:
- **form_response**: İlişkili form cevabı
- **question**: İlişkili soru
- **text_answer**: Metin cevabı
- **numeric_answer**: Sayısal cevap
- **selected_options**: Seçilen seçenekler (Many-to-Many)
- **answer_score**: Cevap puanı (otomatik hesaplanır)

### RiskLevelMapping Modeli
Risk seviyesi eşleştirmeleri:
- **form_type**: Form tipi (DAST-10, SDS, vs.)
- **min_score**: Minimum puan
- **max_score**: Maksimum puan
- **risk_level**: Risk seviyesi adı
- **description**: Açıklama
- **recommendations**: Öneriler

## Soru Tipleri ve Frontend Karşılıkları

Form sistemi 8 farklı soru tipini destekler:

| Soru Tipi | Frontend Karşılığı | Veri Alanı | Açıklama |
|-----------|-------------------|------------|-----------|
| `text` | Text input | `text_answer` | Kısa metin girişi |
| `yes_no` | Radio (Evet/Hayır) | `numeric_answer` | İkili seçim (0/1) |
| `scale` | Slider | `numeric_answer` | 0-4 arası ölçek değeri |
| `single_choice` | Radio (A/B/C/D) | `selected_options` | Tek seçim |
| `multiple_choice` | Checkbox | `selected_options` | Çoklu seçim |
| `number` | Number input | `numeric_answer` | Sayısal giriş |
| `date` | Date picker | `text_answer` | Tarih girişi (YYYY-MM-DD) |
| `textarea` | Textarea | `text_answer` | Uzun metin girişi |

## Skorlama Sistemi

### Otomatik Puan Hesaplama
- **Form kaydında**: `calculate_risk_level()` metodu otomatik çalışır
- **Cevap kaydında**: `calculate_score()` metodu puanları hesaplar
- **Yüzde hesaplama**: `(total_score / max_score) * 100`

### Puanlama Tipleri
- **binary**: Evet/Hayır soruları (0-1 puan)
- **scale**: Ölçek soruları (0-4 puan)
- **weighted**: Ağırlıklı puanlama
- **custom**: Özel puanlama kuralları
- **none**: Puanlama yok

## Risk Hesaplama

### DAST-10 Risk Seviyeleri (0-10 puan)
- **0-2 puan**: "Madde Kullanımı Yok veya Çok Düşük"
- **3-5 puan**: "Orta Risk"
- **6-8 puan**: "Yüksek Risk"
- **9-10 puan**: "Çok Yüksek Risk"

### SDS Risk Seviyeleri (0-20 puan)
- **0-4 puan**: "Düşük Bağımlılık Belirtisi"
- **5-7 puan**: "Orta Düzey Bağımlılık Belirtisi"
- **8-20 puan**: "Yüksek Bağımlılık Belirtisi"

### Risk Level Mapping
Admin panelinden farklı form tipleri için risk seviyesi eşleştirmeleri yapılabilir.

## Form Tipleri

### 1. DAST-10 Madde Kullanımı Tarama Testi
- **Amaç**: Madde kullanımının risk seviyesini ölçmek
- **Soru sayısı**: 10 soru
- **Puanlama**: Binary (0-1 puan/soru)
- **Toplam puan**: 0-10
- **Soru tipi**: yes_no

### 2. SDS Esrar Bağımlılık Şiddeti Ölçeği
- **Amaç**: Esrar bağımlılığının şiddetini ölçmek
- **Soru sayısı**: 5 soru
- **Puanlama**: Scale (0-4 puan/soru)
- **Toplam puan**: 0-20
- **Soru tipi**: scale

### 3. Genel Sağlık Değerlendirme Formu
- **Amaç**: Kullanıcıların genel sağlık durumlarını değerlendirmek
- **Soru sayısı**: 5 soru
- **Puanlama**: Karışık (yes_no + single_choice)
- **Toplam puan**: 0-5
- **Soru tipleri**: yes_no, single_choice

## Form Doldurma Sonrası Elde Edilen Veriler

### Temel Skorlar
- **total_score**: Formun toplam puanı
- **percentage_score**: Yüzde olarak puan (0-100%)
- **risk_level**: Otomatik hesaplanan risk seviyesi

### Yorumlama ve Öneriler
- **interpretation**: Otomatik oluşturulan yorum metni
- **recommendations**: Kişiselleştirilmiş öneriler
- **submitted_at**: Form gönderilme tarihi

### Cevap Detayları
Her soru için:
- Soru metni ve tipi
- Verilen cevap (text, numeric veya selected options)
- Cevap puanı (answer_score)

## Özellikler

- **Farklı Soru Tipleri**: 8 farklı soru tipi desteği
- **Otomatik Skorlama**: Soru ve form seviyesinde otomatik puan hesaplama
- **Risk Değerlendirmesi**: DAST ve SDS için özelleşmiş risk hesaplama
- **Authentication Koruması**: Sadece giriş yapmış kullanıcılar formlara erişebilir
- **Form Yönetimi**: Admin panelinden form ve soru oluşturma/düzenleme
- **Cevap Takibi**: Kullanıcıların form cevaplarını görüntüleme
- **Tek Seferlik Doldurma**: Bir kullanıcı bir formu sadece bir kez doldurabilir
- **Aşamalı Formlar**: Stage sistemi ile adım adım form doldurma
- **Ölçek Etiketleri**: Scale soruları için özelleştirilebilir etiketler

## Admin Panel

Admin panelinden aşağıdaki işlemleri gerçekleştirebilirsiniz:

### Form Yönetimi
- Form oluşturma/düzenleme
- Form aktiflik durumu yönetimi
- Puanlama sistemi konfigürasyonu
- Talimat ve disclaimer metinleri

### Soru Yönetimi
- Soru ekleme/düzenleme
- Soru tipi seçimi
- Zorunlu soru işaretleme
- Sıralama düzenleme
- Puan ağırlığı belirleme

### Seçenek Yönetimi
- Çoktan seçmeli sorular için seçenek ekleme
- Seçenek puan değerleri belirleme
- Seçenek sıralama

### Risk Seviyesi Yönetimi
- Farklı form tipleri için risk eşleştirmeleri
- Risk seviyesi açıklamaları ve önerileri
- Aktif/pasif risk kuralları

### Cevap Görüntüleme
- Kullanıcı form cevaplarını görüntüleme
- Skor ve risk seviyesi analizi
- Cevap detaylarını inceleme

## Güvenlik

- Tüm endpoint'ler authentication gerektirir
- Kullanıcılar sadece kendi form cevaplarını görüntüleyebilir
- Bir kullanıcı bir formu sadece bir kez doldurabilir
- Form validasyonu backend'de yapılır
- Admin kullanıcılar tüm formları, normal kullanıcılar sadece aktif formları görebilir

## Veritabanı Kısıtlamaları

- **Form-User**: Her kullanıcı bir formu sadece bir kez doldurabilir (`unique_together`)
- **FormResponse-Question**: Bir form cevabında her soru sadece bir kez cevaplanabilir (`unique_together`)
- **QuestionOption**: Seçenekler soruya göre sıralanır (`ordering`)
- **RiskLevelMapping**: Risk seviyeleri form tipine göre sıralanır (`ordering`)
