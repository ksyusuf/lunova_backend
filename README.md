# Lunova Backend

Bu dizin, Lunova projesinin Django tabanlı backend uygulamasını içerir.

## Gereksinimler
- Python 3.11+
- pip
- (Tavsiye edilen) virtualenv veya venv

## Ortam Değişkenleri (.env)
Aşağıdaki ortam değişkenlerini içeren bir `.env` dosyası oluşturmalısınız (örnek):

```
DB_NAME=***
DB_USER=***
DB_PASSWORD=***
DB_HOST=localhost
DB_PORT=5432
ENVIRONMENT=Development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
MEDIA_URL=/media/
MEDIA_ROOT=/media/
SECRET_KEY=***
```

> **Not:** Gerekli değişkenler projenizin ayarlarına göre değişebilir. `DJANGO_SECRET_KEY` zorunludur. `DATABASE_URL` yoksa varsayılan olarak `db.sqlite3` kullanılır.

## Kurulum ve Çalıştırma
1. **Dizine girin:**
   ```bash
   cd backend
   ```
2. **Sanal ortam oluşturun ve aktif edin:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. **Gereksinimleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```
   
4. **.env dosyasını oluşturun:**
   Proje kök dizinine `.env` dosyasını ekleyin ve yukarıdaki örneğe göre doldurun.

5. **Veritabanı migrasyonlarını çalıştırın:**
   ```bash
   python manage.py migrate
   ```

6. **Geliştirme sunucusunu başlatın:**
   ```bash
   python manage.py runserver
   ```

Sunucu başlatıldığında, [http://127.0.0.1:8000](http://127.0.0.1:8000) adresinden projeye erişebilirsiniz.

---

Herhangi bir sorunla karşılaşırsanız, hata mesajını kontrol edin ve eksik bağımlılıkları yükleyin veya ortam değişkenlerini gözden geçirin. 

## SECRET_KEY Nasıl Oluşturulur?

Django projelerinde güvenlik için gizli bir anahtar (SECRET_KEY) gereklidir. Kendi anahtarınızı oluşturmak için aşağıdaki adımları izleyin:

1. Aşağıdaki komutu terminalde çalıştırın:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Bu komut size rastgele ve güvenli bir SECRET_KEY üretecektir.

2. Üretilen anahtarı kopyalayın ve `.env` dosyanıza aşağıdaki gibi ekleyin:
   ```env
   SECRET_KEY=buraya-olusan-anahtari-yapistirin
   ```

> `.env` dosyanız asla versiyon kontrolüne (git) eklenmemelidir. Her geliştirici kendi anahtarını oluşturmalıdır. 