# Appointment API Test Results
Generated at: 2025-08-17 17:33:07.777339

## Login expert
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/accounts/login/
- Payload:
```json
{
  "email": "ozel_@expert.com",
  "password": "yusuf123"
}
```
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1NjA0NTk4NiwiaWF0IjoxNzU1NDQxMTg2LCJqdGkiOiJjZDU2ODA2ZWJiMjg0Zjc0YWI5N2U5NWE3ZTUyODY4NCIsInVzZXJfaWQiOiIyMSJ9.yoQXncF5sCKvKzJUV3ckEMekMd6hPW5Yx9nOgT0dQhQ",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU1NDQyMDg2LCJpYXQiOjE3NTU0NDExODYsImp0aSI6ImM5MzI5NTI0ZDkxNzQwMThiN2ZiODUyZmM0NTMwMWNiIiwidXNlcl9pZCI6IjIxIn0.908AW7-ygfsRceLtsk-Gvsg9NimbS9gnZAEPtPiG8oE",
  "email": "ozel_@expert.com"
}
```

## Login client
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/accounts/login/
- Payload:
```json
{
  "email": "ozel_@client.com",
  "password": "yusuf123"
}
```
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1NjA0NTk4NywiaWF0IjoxNzU1NDQxMTg3LCJqdGkiOiIzMDllMTM4NzIxNGY0ZjgxOTA1Y2QxZGM1MTAzMDM5NiIsInVzZXJfaWQiOiIyMiJ9.hsHEqJG0Bqcbs80FvBN590SkwSMt8P2qKXXA5_eCV7E",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU1NDQyMDg3LCJpYXQiOjE3NTU0NDExODcsImp0aSI6ImEzMThmYjdjYTNlMjRhN2RiZDc5MzI2MmNlMDU2YWJiIiwidXNlcl9pZCI6IjIyIn0.1VUb7YLU71HND-9HWCOyJ8ik3wX7ppYfNNT5o121MZI",
  "email": "ozel_@client.com"
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
  "date": "2025-08-20",
  "time": "14:00:00",
  "duration": 60
}
```
- Status Code: 201
- Expected Status: 201
- Passed: True ✅
```json
{
  "id": 55,
  "expert": 21,
  "client": 22,
  "expert_name": "yusuf expert",
  "client_name": "yusuf client",
  "date": "2025-08-20",
  "time": "14:00:00",
  "duration": 60,
  "is_confirmed": false,
  "notes": null,
  "status": "pending",
  "zoom_start_url": "mock url",
  "zoom_join_url": "mock url",
  "zoom_meeting_id": "mock url",
  "created_at": "2025-08-17T14:33:07.173242Z",
  "updated_at": "2025-08-17T14:33:07.175271Z"
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
  "date": "2025-08-20",
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
  "date": "2025-08-21",
  "time": "10:00:00",
  "duration": 45
}
```
- Status Code: 201
- Expected Status: 201
- Passed: True ✅
```json
{
  "id": 56,
  "expert": 21,
  "client": 22,
  "expert_name": "yusuf expert",
  "client_name": "yusuf client",
  "date": "2025-08-21",
  "time": "10:00:00",
  "duration": 45,
  "is_confirmed": false,
  "notes": null,
  "status": "pending",
  "zoom_start_url": "mock url",
  "zoom_join_url": "mock url",
  "zoom_meeting_id": "mock url",
  "created_at": "2025-08-17T14:33:07.245239Z",
  "updated_at": "2025-08-17T14:33:07.248013Z"
}
```

## expert POST Onaylanmamış Randevuyu Onaylama Girişimi
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/56/approve/
- Status Code: 400
- Expected Status: 400
- Passed: True ✅
```json
{
  "error": "Bu randevu onay bekleyen durumda değil"
}
```

## expert POST Randevuyu Onaylama
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/56/confirm/
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
{
  "id": 56,
  "expert": 21,
  "client": 22,
  "expert_name": "yusuf expert",
  "client_name": "yusuf client",
  "date": "2025-08-21",
  "time": "10:00:00",
  "duration": 45,
  "is_confirmed": true,
  "notes": null,
  "status": "confirmed",
  "zoom_start_url": "mock url",
  "zoom_join_url": "mock url",
  "zoom_meeting_id": "mock url",
  "created_at": "2025-08-17T14:33:07.245239Z",
  "updated_at": "2025-08-17T14:33:07.319618Z"
}
```

## expert POST Uzmanın İptal Talebi Oluşturma Girişimi
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/56/cancel-request/
- Status Code: 403
- Expected Status: 403
- Passed: True ✅
```json
{
  "error": "Bu randevu için iptal talebi gönderme yetkiniz yok"
}
```

## expert POST İptal Talebi Olmayan Randevuyu İptal Etme
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/56/cancel-confirm/
- Payload:
```json
{
  "confirm": true
}
```
- Status Code: 400
- Expected Status: 400
- Passed: True ✅
```json
{
  "error": "Bu randevu iptal talebi bekleyen durumda değil"
}
```

## expert DELETE Randevuyu Silme
- Method: DELETE
- URL: http://127.0.0.1:8000/api/v1/appointments/56/
- Status Code: 204
- Expected Status: 204
- Passed: True ✅
```json
""
```

## client POST Randevu Talebi Oluşturma (başarılı)
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/client/request/
- Payload:
```json
{
  "expert": 21,
  "date": "2025-08-22",
  "time": "11:00:00",
  "duration": 30
}
```
- Status Code: 201
- Expected Status: 201
- Passed: True ✅
```json
{
  "id": 57,
  "expert": 21,
  "expert_name": "yusuf expert",
  "client_name": "yusuf client",
  "date": "2025-08-22",
  "time": "11:00:00",
  "duration": 30,
  "notes": null,
  "status": "waiting_approval",
  "created_at": "2025-08-17T14:33:07.460535Z",
  "updated_at": "2025-08-17T14:33:07.460535Z"
}
```

## client POST Aynı Randevu Talebini Tekrar Oluşturma
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/client/request/
- Payload:
```json
{
  "expert": 21,
  "date": "2025-08-22",
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
  "date": "2025-08-22",
  "time": "11:00:00",
  "duration": 30
}
```
- Status Code: 403
- Expected Status: 403
- Passed: True ✅
```json
{
  "error": "Sadece danışanlar bu endpoint'i kullanabilir. Mevcut rol: expert"
}
```

## client POST Farklı Randevu Talebi Oluşturma
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/client/request/
- Payload:
```json
{
  "expert": 21,
  "date": "2025-08-23",
  "time": "12:00:00",
  "duration": 60
}
```
- Status Code: 201
- Expected Status: 201
- Passed: True ✅
```json
{
  "id": 58,
  "expert": 21,
  "expert_name": "yusuf expert",
  "client_name": "yusuf client",
  "date": "2025-08-23",
  "time": "12:00:00",
  "duration": 60,
  "notes": null,
  "status": "waiting_approval",
  "created_at": "2025-08-17T14:33:07.565836Z",
  "updated_at": "2025-08-17T14:33:07.565836Z"
}
```

## expert POST Randevu Talebini Onaylama
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/58/approve/
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
{
  "id": 58,
  "expert": 21,
  "client": 22,
  "expert_name": "yusuf expert",
  "client_name": "yusuf client",
  "date": "2025-08-23",
  "time": "12:00:00",
  "duration": 60,
  "is_confirmed": true,
  "notes": null,
  "status": "confirmed",
  "zoom_start_url": "confirm mock url",
  "zoom_join_url": "confirm mock url",
  "zoom_meeting_id": "confirm mock url",
  "created_at": "2025-08-17T14:33:07.565836Z",
  "updated_at": "2025-08-17T14:33:07.602697Z"
}
```

## expert POST Onaylanmış Randevuyu Tekrar Onaylama
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/58/confirm/
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
{
  "id": 58,
  "expert": 21,
  "client": 22,
  "expert_name": "yusuf expert",
  "client_name": "yusuf client",
  "date": "2025-08-23",
  "time": "12:00:00",
  "duration": 60,
  "is_confirmed": true,
  "notes": null,
  "status": "confirmed",
  "zoom_start_url": "confirm mock url",
  "zoom_join_url": "confirm mock url",
  "zoom_meeting_id": "confirm mock url",
  "created_at": "2025-08-17T14:33:07.565836Z",
  "updated_at": "2025-08-17T14:33:07.638608Z"
}
```

## client GET Danışanın Toplantı Bilgilerini Görüntülemesi
- Method: GET
- URL: http://127.0.0.1:8000/api/v1/appointments/58/meeting-info/
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
{
  "appointment_id": 58,
  "meeting_id": "confirm mock url",
  "start_url": "confirm mock url",
  "join_url": "confirm mock url",
  "topic": "Danışmanlık: yusuf client - Uzman yusuf expert",
  "date": "2025-08-23",
  "time": "12:00:00",
  "duration": 60,
  "is_confirmed": true,
  "status": "confirmed"
}
```

## client POST Randevu İptal Talebi Gönderme
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/58/cancel-request/
- Status Code: 200
- Expected Status: 200
- Passed: True ✅
```json
{
  "id": 58,
  "status": "cancel_requested",
  "message": "İptal talebi gönderildi, uzman onayı bekleniyor."
}
```

## client POST Danışanın İptal Talebini Onaylama Girişimi
- Method: POST
- URL: http://127.0.0.1:8000/api/v1/appointments/58/cancel-confirm/
- Payload:
```json
{
  "confirm": true
}
```
- Status Code: 403
- Expected Status: 403
- Passed: True ✅
```json
{
  "error": "Bu randevunun iptal talebini değerlendirme yetkiniz yok"
}
```

## client DELETE Randevuyu Silme
- Method: DELETE
- URL: http://127.0.0.1:8000/api/v1/appointments/58/
- Status Code: 204
- Expected Status: 204
- Passed: True ✅
```json
""
```

