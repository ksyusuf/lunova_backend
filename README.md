# Lunova Backend

## Geliştirme (Development) Ortamı

> **Not:** Aşağıdaki işlemlere başlamadan önce sanal ortamı aktive etmelisin.
> - Windows: `venv\Scripts\activate`
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

3. Veritabanı migrasyonlarını uygula:
   ```bash
   python manage.py migrate
   ```

4. Geliştirme sunucusunu başlat:
   ```bash
   python manage.py runserver
   ```

---

## Production Ortamı

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
> - Windows: `venv\Scripts\activate`
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

## Ekstra Notlar

- `.env` ve `.env.production` dosyalarını asla git'e ekleme! (Zaten .gitignore'da olmalı)
- Migration ve collectstatic işlemlerini production deploy öncesi mutlaka yap.
- Sorun yaşarsan veya özel bir servis dosyası (systemd, pm2, vs.) örneği istersen, README'yi güncelleyebilirsin. 
