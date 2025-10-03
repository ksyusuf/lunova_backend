# Lunova Backend

## Geliştirme (Development) Ortamı

> **Not:** Aşağıdaki işlemlere başlamadan önce sanal ortamı aktive etmelisin.
> - Windows: `.venv/Scripts/activate`
> - Mac/Linux: `source venv/bin/activate`

1. Gerekli bağımlılıkları yükle:
   ```bash
   pip install -r requirements.txt
   ```

2. Ana dizinde `.env` dosyanı bulundur. Örnek bir `.env` dosyası:
   ```env
   SECRET_KEY=senin_secret_keyin
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_NAME=veritabani_adi
   DB_USER=kullanici_adi
   DB_PASSWORD=sifre
   DB_HOST=localhost
   DB_PORT=5432
   ENVIRONMENT=Development
   ```

   migration işlemleri uygulanamdan önce lokalindeki kullanıcı için grant yetkisi ver.
   ```bash
   GRANT ALL ON SCHEMA public TO lunova;
   GRANT ALL PRIVILEGES ON DATABASE "lunova-test" TO lunova;
   ```
   
3. Veritabanı migrasyonlarını oluştur:
   ```bash
   python manage.py makemigrations
   ```
 
4. Veritabanı migrasyonlarını uygula:
   ```bash
   python manage.py migrate
   ```

4,5. Veritabanı Besleme
   Eğer ilk kez  veritabanı kuruyorsanız, lokal çalışma için veritabanını beslemelisiniz.
   ```bash
   python accounts/db_feed.py
   python availability/scripts/feed_availability.py
   python forms/management/commands/create_sample_forms.py
   ```

5. Geliştirme sunucusunu başlat:
   ```bash
   python manage.py runserver
   ```

http://localhost:8000/admin/

---

## Production Ortamı

yeni kurulum durumunda veritabanının beslenmesi gerekecek, railway'e bu şekilde bağlanıp feed çalıştırılabilir.
link işlemi yapılırken proje ana dizininde olmaya dikkat et.
link yaparken ilgili servisi seçmen gerek.

```bash
railway link
railway ssh python accounts/db_feed.py
railway ssh python availability/scripts/feed_availability.py
railway ssh python forms/management/commands/create_sample_forms.py
```

1. Ana dizinde **sadece** `.env.production` dosyanı bulundur. Örnek bir `.env.production` dosyası:
   ```env
   SECRET_KEY=guclu_secret_key
   DEBUG=False
   ALLOWED_HOSTS=senin_domainin.com
   DB_NAME=prod_db_adi
   DB_USER=prod_kullanici
   DB_PASSWORD=prod_sifre
   DB_HOST=localhost
   DB_PORT=5432
   ENVIRONMENT=Production
   ```

> **Not:** Aşağıdaki işlemlere başlamadan önce sanal ortamı aktive etmelisin.
> - Windows: `.venv/Scripts/activate`
> - Mac/Linux: `source venv/bin/activate`

2. Gerekli bağımlılıkları yükle:
   ```bash
   pip install -r requirements.txt
   ```

3. Veritabanı migrasyonlarını uygula:
   ```bash
   python manage.py migrate
   ```

4. Statik dosyaları topla:
   ```bash
   python manage.py collectstatic
   ```

5. **Production sunucusunu başlatmak için:**
   - Sunucuyu başlat:
     ```bash
     python serve.py
     ```

---

## Ortam Dosyası Yönetimi

- **Development ortamında:** Sadece `.env` dosyası bulundur.
- **Production ortamında:** Sadece `.env.production` dosyası bulundur.
- Her iki dosya da varsa, `.env.production` öncelikli olarak okunur.
- Ortam değişkeni ayarlamaya gerek yoktur; dosya varlığına göre ortam otomatik belirlenir.

---

## Apps

### Accounts
- Kullanıcı yönetimi ve authentication
- Client, Expert, Admin profilleri

### Zoom
- Zoom meeting entegrasyonu
- Uzmanlar için meeting oluşturma

### Appointments
- Randevu yönetimi sistemi
- Client-Expert randevu takibi

### Forms
- Dinamik form sistemi
- Farklı soru tipleri (text, test, çok seçimli)
- Authentication korumalı API endpoints

### Availability
- Kullanıcıların haftalık ve istisnai müsaitlik durumları
- İstisnai müsaitlik -> Ekstra / İptal

## Ekstra Notlar

- `.env` ve `.env.production` dosyalarını asla git'e ekleme! (Zaten .gitignore'da olmalı)
- Migration ve collectstatic işlemlerini production deploy öncesi mutlaka yap.
- Sorun yaşarsan veya özel bir servis dosyası (systemd, pm2, vs.) örneği istersen, README'yi güncelleyebilirsin. 
