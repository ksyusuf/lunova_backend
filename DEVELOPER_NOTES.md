# Geliştirici Notları

## PostgreSQL Sürücüsü

- Bu projede PostgreSQL veritabanı bağlantısı için **psycopg2** Python modülü kullanılmaktadır.
- Production ve development ortamlarında requirements.txt dosyasına `psycopg2` eklenmelidir.

## Kurulum Notu

- Production ortamında psycopg2 kurmak için sistemde C derleyicisi ve PostgreSQL development kütüphaneleri bulunmalıdır.
- Ubuntu için örnek kurulum:
  ```bash
  sudo apt-get install libpq-dev python3-dev build-essential
  pip install psycopg2
  ``` 