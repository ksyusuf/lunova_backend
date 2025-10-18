# Appointment API Test Results
Generated at: 2025-10-18 20:44:25.360096

## Login expert
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/accounts/login/
- Payload:
```json
{
  "email": "expert2@example.com",
  "password": "password123"
}
```
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MTQxNDI2NCwiaWF0IjoxNzYwODA5NDY0LCJqdGkiOiI3NjhmYzI5MzE0NTk0YTU0YjIwYjlkY2RjYmQwYzk1MiIsInVzZXJfaWQiOiIyIn0.8eA2sM9P1mgvVSlLjGfQX-aQ5TzgMAUNqqpmGA7ug3k",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYwODEwMzY0LCJpYXQiOjE3NjA4MDk0NjQsImp0aSI6ImM3MTE5NDI1YmI2NzQ0NTE4MjM3NTZmZDczN2IzZGQ0IiwidXNlcl9pZCI6IjIifQ.Dniz5OjIZFtKbv0w5z8jVSfhyy7yYWOYxnnbrs-oaOM",
  "email": "expert2@example.com",
  "role": "expert"
}
```

## Login client
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/accounts/login/
- Payload:
```json
{
  "email": "client5@example.com",
  "password": "password123"
}
```
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MTQxNDI2NCwiaWF0IjoxNzYwODA5NDY0LCJqdGkiOiJiZDgzMzY0NzEzZTI0ZWQyODczOTE1NjYxNjkwYTYxOCIsInVzZXJfaWQiOiIyNSJ9.fg039j2XpOC2M7oqVBgqnE71o-VCiqjSISWVcdCiSUc",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYwODEwMzY0LCJpYXQiOjE3NjA4MDk0NjQsImp0aSI6IjM2ZThiMDQ3YTI3YTRlNGE4Y2EzNDQyMzZiYjVjZDg0IiwidXNlcl9pZCI6IjI1In0.sLcSBNJMR5TrhYCnIm3raVksg0QH5mqBAzGvx3jGYNo",
  "email": "client5@example.com",
  "role": "client"
}
```

## expert POST Randevu Oluşturma (başarılı)
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/expert/create/
- Payload:
```json
{
  "expert": 21,
  "client": 22,
  "date": "2025-10-20",
  "time": "14:00:00",
  "duration": 60
}
```
- Status Code: 201
- Expected Status: 201
- Passed: True ✅
```json
{
  "id": 211,
  "expert": 21,
  "client": 22,
  "expert_name": "Hatice Rodriguez",
  "client_name": "William Öztürk",
  "date": "2025-10-20",
  "time": "14:00:00",
  "duration": 60,
  "is_confirmed": false,
  "notes": null,
  "status": "pending",
  "zoom_start_url": "mock url",
  "zoom_join_url": "mock url",
  "zoom_meeting_id": "mock url",
  "created_at": "2025-10-18T17:44:24.493464Z",
  "updated_at": "2025-10-18T17:44:24.495469Z"
}
```

## expert POST Aynı Randevuyu Tekrar Oluşturma
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/expert/create/
- Payload:
```json
{
  "expert": 21,
  "client": 22,
  "date": "2025-10-20",
  "time": "14:00:00",
  "duration": 60
}
```
- Status Code: 400
- Expected Status: 400
- Passed: True ✅
```json
{
  "non_field_errors": [
    "Bu tarih ve saatte uzmanın başka bir randevusu bulunmaktadır."
  ]
}
```

## expert POST Farklı Randevu Oluşturma
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/expert/create/
- Payload:
```json
{
  "expert": 21,
  "client": 22,
  "date": "2025-10-21",
  "time": "10:00:00",
  "duration": 45
}
```
- Status Code: 201
- Expected Status: 201
- Passed: True ✅
```json
{
  "id": 212,
  "expert": 21,
  "client": 22,
  "expert_name": "Hatice Rodriguez",
  "client_name": "William Öztürk",
  "date": "2025-10-21",
  "time": "10:00:00",
  "duration": 45,
  "is_confirmed": false,
  "notes": null,
  "status": "pending",
  "zoom_start_url": "mock url",
  "zoom_join_url": "mock url",
  "zoom_meeting_id": "mock url",
  "created_at": "2025-10-18T17:44:24.583835Z",
  "updated_at": "2025-10-18T17:44:24.586373Z"
}
```

## expert PATCH Beklemede Olan Randevuyu Onaylama
- Method: PATCH
- URL: http://127.0.0.1:8000/api/v1/appointments/212/status/
- Payload:
```json
{
  "status": "confirmed"
}
```
- Status Code: 404
- Expected Status: 200
- Passed: False ❌
```json
{
  "detail": "No Appointment matches the given query."
}
```

## expert PATCH Onaylanmış Randevuyu Tamamlama
- Method: PATCH
- URL: http://127.0.0.1:8000/api/v1/appointments/212/status/
- Payload:
```json
{
  "status": "completed"
}
```
- Status Code: 404
- Expected Status: 200
- Passed: False ❌
```json
{
  "detail": "No Appointment matches the given query."
}
```

## expert PATCH Tamamlanmış Randevuyu Güncelleme Girişimi
- Method: PATCH
- URL: http://127.0.0.1:8000/api/v1/appointments/212/status/
- Payload:
```json
{
  "status": "confirmed"
}
```
- Status Code: 404
- Expected Status: 400
- Passed: False ❌
```json
{
  "detail": "No Appointment matches the given query."
}
```

## expert DELETE Randevuyu Silme
- Method: DELETE
- URL: http://127.0.0.1:8000/api/v1/appointments/212/
- Status Code: 404
- Expected Status: 204
- Passed: False ❌
```json
{
  "detail": "No Appointment matches the given query."
}
```

## client POST Randevu Talebi Oluşturma (başarılı)
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/client/request/
- Payload:
```json
{
  "expert": 21,
  "date": "2025-10-22",
  "time": "11:00:00",
  "duration": 30
}
```
- Status Code: 201
- Expected Status: 201
- Passed: True ✅
```json
{
  "id": 213,
  "expert": 21,
  "expert_name": "Hatice Rodriguez",
  "client_name": "Charles Arslan",
  "date": "2025-10-22",
  "time": "11:00:00",
  "duration": 30,
  "notes": null,
  "status": "waiting_approval",
  "created_at": "2025-10-18T17:44:24.780889Z",
  "updated_at": "2025-10-18T17:44:24.780889Z"
}
```

## client POST Aynı Randevu Talebini Tekrar Oluşturma
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/client/request/
- Payload:
```json
{
  "expert": 21,
  "date": "2025-10-22",
  "time": "11:00:00",
  "duration": 30
}
```
- Status Code: 400
- Expected Status: 400
- Passed: True ✅
```json
{
  "non_field_errors": [
    "Bu tarih ve saatte uzmanın başka bir randevusu bulunmaktadır."
  ]
}
```

## expert POST Uzmanın Danışan Endpoint'ini Kullanma Girişimi
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/client/request/
- Payload:
```json
{
  "expert": 21,
  "date": "2025-10-22",
  "time": "11:00:00",
  "duration": 30
}
```
- Status Code: 400
- Expected Status: 403
- Passed: False ❌
```json
{
  "non_field_errors": [
    "Sadece danışanlar bu şekilde randevu talebi oluşturabilir."
  ]
}
```

## client POST Farklı Randevu Talebi Oluşturma
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/client/request/
- Payload:
```json
{
  "expert": 21,
  "date": "2025-10-23",
  "time": "12:00:00",
  "duration": 60
}
```
- Status Code: 201
- Expected Status: 201
- Passed: True ✅
```json
{
  "id": 214,
  "expert": 21,
  "expert_name": "Hatice Rodriguez",
  "client_name": "Charles Arslan",
  "date": "2025-10-23",
  "time": "12:00:00",
  "duration": 60,
  "notes": null,
  "status": "waiting_approval",
  "created_at": "2025-10-18T17:44:24.895206Z",
  "updated_at": "2025-10-18T17:44:24.895206Z"
}
```

## expert PATCH Randevu Talebini Onaylama
- Method: PATCH
- URL: http://127.0.0.1:8000/api/v1/appointments/214/status/
- Payload:
```json
{
  "status": "confirmed"
}
```
- Status Code: 404
- Expected Status: 200
- Passed: False ❌
```json
{
  "detail": "No Appointment matches the given query."
}
```

## client GET Danışanın Toplantı Bilgilerini Görüntülemesi
- Method: GET
- URL: http://127.0.0.1:8000/api/v1/appointments/214/meeting-info/
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
{
  "appointment_id": 214,
  "meeting_id": null,
  "start_url": null,
  "join_url": null,
  "topic": "Danışmanlık: Charles Arslan - Uzman Hatice Rodriguez",
  "date": "2025-10-23",
  "time": "12:00:00",
  "duration": 60,
  "is_confirmed": false,
  "status": "waiting_approval"
}
```

## client PATCH Randevu İptal Talebi Gönderme
- Method: PATCH
- URL: http://127.0.0.1:8000/api/v1/appointments/214/status/
- Payload:
```json
{
  "status": "cancel_requested"
}
```
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
{
  "id": 214,
  "expert": 21,
  "client": 25,
  "expert_name": "Hatice Rodriguez",
  "client_name": "Charles Arslan",
  "date": "2025-10-23",
  "time": "12:00:00",
  "duration": 60,
  "is_confirmed": false,
  "notes": null,
  "status": "cancel_requested",
  "zoom_start_url": null,
  "zoom_join_url": null,
  "zoom_meeting_id": null,
  "created_at": "2025-10-18T17:44:24.895206Z",
  "updated_at": "2025-10-18T17:44:25.009248Z"
}
```

## expert PATCH İptal Talebini Reddetme
- Method: PATCH
- URL: http://127.0.0.1:8000/api/v1/appointments/214/status/
- Payload:
```json
{
  "status": "confirmed"
}
```
- Status Code: 404
- Expected Status: 200
- Passed: False ❌
```json
{
  "detail": "No Appointment matches the given query."
}
```

## client DELETE Randevuyu Silme
- Method: DELETE
- URL: http://127.0.0.1:8000/api/v1/appointments/214/
- Status Code: 204
- Expected Status: 204
- Passed: True ✅
```json
""
```

## expert GET Tarih Parametresi Olmadan Liste Getirme
- Method: GET
- URL: http://127.0.0.1:8000/api/v1/appointments/
- Status Code: 400
- Expected Status: 400
- Passed: True ✅
```json
{
  "error": "start_date parametresi zorunludur"
}
```

## expert GET Tarih Aralığı ile Randevu Listesi
- Method: GET
- URL: http://127.0.0.1:8000/api/v1/appointments/?start_date=2025-10-01&end_date=2025-10-31
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
[]
```

## expert GET Status Filtresi ile Randevu Listesi
- Method: GET
- URL: http://127.0.0.1:8000/api/v1/appointments/?start_date=2025-10-01&end_date=2025-10-31&status=confirmed
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
[]
```

## client GET Uzmanın Randevularını Danışan Olarak Görüntüleme
- Method: GET
- URL: http://127.0.0.1:8000/api/v1/appointments/experts/21/appointments/?start_date=2025-10-01&end_date=2025-10-31
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
{
  "expert_id": 21,
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "appointments": [
    {
      "id": 211,
      "date": "2025-10-20",
      "start_time": "14:00:00",
      "end_time": "15:30:00",
      "status": "pending"
    },
    {
      "id": 212,
      "date": "2025-10-21",
      "start_time": "10:00:00",
      "end_time": "11:05:00",
      "status": "pending"
    },
    {
      "id": 213,
      "date": "2025-10-22",
      "start_time": "11:00:00",
      "end_time": "11:50:00",
      "status": "waiting_approval"
    }
  ]
}
```

## expert GET Geçersiz Tarih Aralığı
- Method: GET
- URL: http://127.0.0.1:8000/api/v1/appointments/?start_date=2025-10-31&end_date=2025-10-01
- Status Code: 400
- Expected Status: 400
- Passed: True ✅
```json
{
  "error": "start_date, end_date'den büyük olamaz"
}
```

## client GET Maksimum Tarih Aralığı Aşımı
- Method: GET
- URL: http://127.0.0.1:8000/api/v1/appointments/?start_date=2025-10-01&end_date=2026-03-01
- Status Code: 400
- Expected Status: 400
- Passed: True ✅
```json
{
  "error": "Tarih aralığı maksimum 4 ay olabilir"
}
```

## client GET Danışanın Kendi Randevularını Görüntüleme
- Method: GET
- URL: http://127.0.0.1:8000/api/v1/appointments/?start_date=2025-10-01&end_date=2025-10-31
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
[
  {
    "id": 213,
    "expert": 21,
    "client": 25,
    "expert_name": "Hatice Rodriguez",
    "client_name": "Charles Arslan",
    "date": "2025-10-22",
    "time": "11:00:00",
    "duration": 30,
    "is_confirmed": false,
    "notes": null,
    "status": "waiting_approval",
    "zoom_start_url": null,
    "zoom_join_url": null,
    "zoom_meeting_id": null,
    "created_at": "2025-10-18T17:44:24.780889Z",
    "updated_at": "2025-10-18T17:44:24.780889Z"
  }
]
```

