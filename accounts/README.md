Endpoint Kullanım

migration sonrası veri beslemesi

Tüm destek tablolarını (Service, AddictionType, Gender) doldurmak için:

```bash
python accounts/db_feed.py
```

Bu script:
- Service tablosunu terapi türleri ile doldurur
- AddictionType tablosunu bağımlılık türleri ile doldurur  
- Gender tablosunu cinsiyet seçenekleri ile doldurur

Alternatif olarak Django shell'de çalıştırmak için:
```bash
python manage.py shell
exec(open('accounts/db_feed.py').read())
```
