# Lunova Backend

<p align="center">
  <img src="favicon-transparent.png" alt="Lunova Logo" width="80px">
</p>

## 🚀 Geliştirme (Development) Ortamı Kurulumu

Geliştirme ortamını çalıştırmadan önce izlenmesi gereken adımlar aşağıdadır.

> **⚠️ Not:** Aşağıdaki işlemlere başlamadan önce **sanal ortamı (venv)** aktive etmelisin.
> * **Windows:** `.venv/Scripts/activate`
> * **Mac/Linux:** `source venv/bin/activate`

### 1. Bağımlılıkları Yükleme
Projenin ihtiyaç duyduğu tüm Python paketlerini yükleyin:

```
pip install -r requirements.txt
```

### 2. Ortam Değişkenleri
Ana dizinde (`.env`) dosyanızın bulunduğundan emin olun. Gerekli içerik ve değişkenler için başlangıç kitini (starter kit) inceleyin.

### 3. Veritabanı (DB) İşlemleri

#### PostgreSQL Kullanımı İçin Yetkilendirme
(Eğer **Sqlite** tercih ediyorsanız bu adımı **pas geçin**.)

Lokal PostgreSQL servisini kullanıyorsanız, migration işlemlerini uygulamadan önce lokaldeki kullanıcınız için gerekli yetkiyi (grant) vermelisiniz:

```
GRANT ALL ON SCHEMA public TO lunova;
GRANT ALL PRIVILEGES ON DATABASE "lunova-test" TO lunova;
```

#### Veritabanı Migrasyonları
Veritabanı şeması değişikliklerini uygulayın:

```
python manage.py migrate
```

### 4. Veritabanı Besleme (Database Seeding) 💾

Eğer veritabanını **ilk kez kuruyorsanız**, lokal çalışma için veritabanını beslemelisiniz.

> **💡 SQLite Kullanıcısı Notu:** Eğer **SQLite** ile çalışıyorsanız, lokal dosyaların oluşturulması ve minimum başlangıç verilerinin sağlanması için **yalnızca `accounts` beslemesini** yapmanız yeterlidir. Diğerlerini pas geçebilirsiniz.

| Veritabanı Tipi | İhtiyaç Duyulan Komutlar |
| :--- | :--- |
| **SQLite** | Sadece ilk komut (`feed_accounts`) yeterlidir. |
| **PostgreSQL** | Tüm komutlar çalıştırılmalıdır. |

```
# Gerekli Temel Kullanıcı Verileri (ZORUNLUDUR)
python accounts/tests/feed_accounts.py

# Ekstra Uygulama Verileri
python availability/tests/feed_availability.py
python appointments/tests/feed_appointments.py
python forms/tests/feed_forms.py
```

### 5. Geliştirme Sunucusunu Başlatma
Kurulum tamamlandıktan sonra geliştirme sunucusunu başlatın:

```
python manage.py runserver
```

Sunucuya ve Django Yönetici Paneli'ne erişim:

* **API Ana Sayfası:** `http://localhost:8000/`
* **Yönetici Paneli:** `http://localhost:8000/admin/`

---

## 🧩 Uygulamalar (Apps)

Proje içerisindeki temel uygulama modülleri ve görevleri:

### Accounts
* **Kullanıcı yönetimi** ve authentication (kimlik doğrulama)
* Client, Expert, Admin profil tiplerini barındırır

### Zoom
* Zoom meeting entegrasyonu
* Uzmanlar için dinamik **meeting oluşturma** ve yönetimi

### Appointments
* **Randevu yönetim** sistemi
* Client ve Expert arasındaki randevu takibi ve durumu yönetimi

### Forms
* **Dinamik form** oluşturma ve işleme sistemi
* Farklı soru tipleri (text, test, çok seçimli vb.)
* Authentication korumalı **API endpoints** (uç noktalar)

### Availability
* Kullanıcıların (özellikle Expert'lerin) haftalık düzenli **müsaitlik durumlarının** yönetimi
* **İstisnai müsaitlik** durumlarının (ekstra mesai veya iptal edilen zaman dilimleri) yönetimi