# Accounts API Tests

Bu dizin, Accounts API için sadeleştirilmiş bir test scriptini içerir.

## Test Dosyaları

- `test_accounts_complete.py` — Tek kapsamlı script (kayıt, giriş, çıkış, geçersiz kayıt)
- `__init__.py` — Python paket tanımlayıcısı

## Ne Test Ediliyor?

- **Kayıt (Register)**: Expert kullanıcı için başarılı kayıt akışı
- **Geçersiz Kayıt**: Parola uyuşmazlığı, eksik alan, hatalı e‑posta formatı
- **Giriş (Login)**: Başarılı/başarısız giriş senaryoları

## Önemli Davranışlar

- **Sadece Development’ta çalışır**: `ENVIRONMENT=Development` ya da `DEBUG=true` değilse script çalışmaz
- **Rastgele veri üretimi**: E‑posta ve T.C. Kimlik No test sırasında dinamik oluşturulur
- **Refresh token cookie**: Login yanıtındaki refresh token session cookie olarak saklanır

## Gereksinimler

1. Django server çalışıyor: `python manage.py runserver`
2. Bağımlılıklar kurulu: `pip install -r requirements.txt`
3. Veritabanı hazır: `python manage.py migrate`
4. Ortam değişkeni: `ENVIRONMENT=Development` veya `DEBUG=true`

## Çalıştırma

Proje kök dizininden:
```bash
python accounts/tests/test_accounts_complete.py
```

Ya da test dizininden:
```bash
cd accounts/tests
python test_accounts_complete.py
```

## Notlar

- Testler, API’yi HTTP üzerinden çağırır (`base_url` varsayılanı `http://127.0.0.1:8000`)
- Üretilen test verileri (e‑posta, TCKN) benzersiz olacak şekilde timestamp ve rastgele değerler içerir
- Konsolda her adım için PASS/FAIL ve detay mesajı gösterilir
