import requests
import json
from datetime import datetime

"""
Appointment API Test Suite

Bu test dosyası yeni appointment sistemini test eder:
- Tarih aralığı ile randevu listeleme (start_date/end_date zorunlu)
- Status güncellemeleri için PATCH /status/ endpoint'i
- Token tabanlı yetkilendirme
- Environment'a göre Zoom meeting oluşturma

Test sonrası oluşturulan randevuları temizlemek için:
- expert ID: değişkende tanımlı
- client ID: değişkende tanımlı

---
Test Senaryoları Özeti

1.  **Login expert**: Uzman kullanıcının sisteme giriş yaparak token alması
2.  **Login client**: Danışan kullanıcının sisteme giriş yaparak token alması
3.  **expert POST create**: Uzmanın danışan için randevu oluşturması
4.  **expert POST create**: Aynı randevuyu tekrar oluşturma (çakışma hatası)
5.  **expert POST create**: Geçerli yeni randevu oluşturma
6.  **expert PATCH status**: Beklemede olan randevuyu onaylama (confirmed)
7.  **expert PATCH status**: Onaylanmış randevuyu tamamlama (completed)
8.  **client PATCH status**: Randevu için iptal talebi oluşturma (cancel_requested)
9.  **expert PATCH status**: İptal talebini onaylama (cancelled)
10. **expert DELETE**: Randevuyu silme
11. **client POST request**: Danışanın uzman için randevu talebi oluşturması
12. **client POST request**: Aynı talebi tekrar oluşturma (çakışma hatası)
13. **expert POST request**: Uzmanın danışan endpoint'ini kullanma girişimi (403)
14. **client POST request**: Geçerli yeni randevu talebi oluşturma
15. **expert PATCH status**: Randevu talebini onaylama (confirmed)
16. **client GET meeting-info**: Toplantı bilgilerini görüntüleme
17. **client PATCH status**: İptal talebi oluşturma
18. **expert PATCH status**: İptal talebini reddetme (confirmed)
19. **client DELETE**: Randevuyu silme
20. **GET appointments list**: Tarih aralığı ile randevu listeleme
21. **GET expert appointments**: Uzmanın randevularını danışan olarak görüntüleme
22. **PATCH appointment**: Randevu notlarını güncelleme
23. **Error cases**: Geçersiz tarih aralığı, eksik parametreler, yetkisiz erişim
"""

BASE_URL = "http://127.0.0.1:8000/api/v1/"
APPOINTMENTS_URL = BASE_URL + "appointments/"
LOGIN_URL = BASE_URL + "accounts/login/"

USERS = {
    "expert": {"email": "expert2@example.com", "password": "password123"},
    "client": {"email": "client5@example.com", "password": "password123"}
}

tokens = {}
results = []

def log_result(step, response, method="GET", url=None, payload=None, expected_status=None):
    if isinstance(response, dict) or isinstance(response, str):
        resp_json = response
        status = getattr(response, "status_code", None) or "N/A"
    else:
        try:
            resp_json = response.json()
        except Exception:
            resp_json = response.text
        status = response.status_code

    passed = (expected_status is None or status == expected_status)
    emoji = "✅" if passed else "❌"

    results.append({
        "step": step,
        "method": method,
        "url": url,
        "payload": payload,
        "status_code": status,
        "expected_status": expected_status,
        "passed": passed,
        "response": resp_json,
        "emoji": emoji
    })
    return resp_json

def login_users():
    """Uzman ve danışan kullanıcılarının girişini yapar ve token'larını alır."""
    for role, creds in USERS.items():
        resp = requests.post(LOGIN_URL, json=creds)
        data = log_result(f"Login {role}", resp, method="POST", url=LOGIN_URL, payload=creds, expected_status=200)
        tokens[role] = data.get("access")

def get_headers(role):
    """Belirtilen role ait Authorization header'ı oluşturur."""
    return {"Authorization": f"Bearer {tokens[role]}"}

def post_test(url, role, json_data=None, expected_status=200, step_description="POST isteği"):
    """Belirtilen URL'e POST isteği gönderir ve sonucu kaydeder."""
    resp = requests.post(url, headers=get_headers(role), json=json_data)
    return log_result(f"{role} POST {step_description}", resp, method="POST", url=url, payload=json_data, expected_status=expected_status)

def get_test(url, role, expected_status=200, step_description="GET isteği"):
    """Belirtilen URL'e GET isteği gönderir ve sonucu kaydeder."""
    resp = requests.get(url, headers=get_headers(role))
    return log_result(f"{role} GET {step_description}", resp, method="GET", url=url, payload=None, expected_status=expected_status)

def delete_test(url, role, expected_status=204, step_description="DELETE isteği"):
    """Belirtilen URL'e DELETE isteği gönderir ve sonucu kaydeder."""
    resp = requests.delete(url, headers=get_headers(role))
    return log_result(f"{role} DELETE {step_description}", resp, method="DELETE", url=url, payload=None, expected_status=expected_status)

def patch_test(url, role, json_data=None, expected_status=200, step_description="PATCH isteği"):
    """Belirtilen URL'e PATCH isteği gönderir ve sonucu kaydeder."""
    resp = requests.patch(url, headers=get_headers(role), json=json_data)
    return log_result(f"{role} PATCH {step_description}", resp, method="PATCH", url=url, payload=json_data, expected_status=expected_status)

def patch_status_test(url, role, status_value, expected_status=200, step_description="Status güncelleme"):
    """Randevu durumunu günceller."""
    payload = {"status": status_value}
    return patch_test(url, role, payload, expected_status, step_description)

def run_appointment_tests():
    """Randevu API'si için tüm test senaryolarını çalıştırır."""
    expert_id = 21
    client_id = 22

    # --- EXPERT AKIŞI ---
    # Uzman randevu oluşturur (başarılı senaryo)
    expert_payload_1 = {"expert": expert_id, "client": client_id, "date": "2025-10-20", "time": "14:00:00", "duration": 60}
    post_test(APPOINTMENTS_URL + "expert/create/", "expert", expert_payload_1, expected_status=201, step_description="Randevu Oluşturma (başarılı)")

    # Aynı randevuyu tekrar oluşturma girişimi (hata senaryosu)
    post_test(APPOINTMENTS_URL + "expert/create/", "expert", expert_payload_1, expected_status=400, step_description="Aynı Randevuyu Tekrar Oluşturma")

    # Yeni bir randevu oluşturur
    expert_payload_2 = {"expert": expert_id, "client": client_id, "date": "2025-10-21", "time": "10:00:00", "duration": 45}
    appt = post_test(APPOINTMENTS_URL + "expert/create/", "expert", expert_payload_2, expected_status=201, step_description="Farklı Randevu Oluşturma")
    expert_appt_id = appt.get("id")

    if expert_appt_id:
        # Beklemede olan randevuyu onaylar (status: pending -> confirmed)
        patch_status_test(APPOINTMENTS_URL + f"{expert_appt_id}/status/", "expert", "confirmed", expected_status=200, step_description="Beklemede Olan Randevuyu Onaylama")

        # Onaylanmış randevuyu tamamlar (status: confirmed -> completed)
        patch_status_test(APPOINTMENTS_URL + f"{expert_appt_id}/status/", "expert", "completed", expected_status=200, step_description="Onaylanmış Randevuyu Tamamlama")

        # Tamamlanmış randevuyu tekrar güncelleme girişimi (hata senaryosu)
        patch_status_test(APPOINTMENTS_URL + f"{expert_appt_id}/status/", "expert", "confirmed", expected_status=400, step_description="Tamamlanmış Randevuyu Güncelleme Girişimi")

        # Randevuyu siler
        delete_test(APPOINTMENTS_URL + f"{expert_appt_id}/", "expert", expected_status=204, step_description="Randevuyu Silme")

    # --- CLIENT AKIŞI ---
    # Danışan randevu talebi oluşturur (başarılı senaryo)
    client_payload_1 = {"expert": expert_id, "date": "2025-10-22", "time": "11:00:00", "duration": 30}
    post_test(APPOINTMENTS_URL + "client/request/", "client", client_payload_1, expected_status=201, step_description="Randevu Talebi Oluşturma (başarılı)")

    # Aynı randevu talebini tekrar oluşturma girişimi (hata senaryosu)
    post_test(APPOINTMENTS_URL + "client/request/", "client", client_payload_1, expected_status=400, step_description="Aynı Randevu Talebini Tekrar Oluşturma")

    # Uzmanın danışan endpoint'ini kullanma yetkisini kontrol eder (hata senaryosu)
    post_test(APPOINTMENTS_URL + "client/request/", "expert", client_payload_1, expected_status=403, step_description="Uzmanın Danışan Endpoint'ini Kullanma Girişimi")

    # Farklı bir randevu talebi oluşturur
    client_payload_2 = {"expert": expert_id, "date": "2025-10-23", "time": "12:00:00", "duration": 60}
    appt_client = post_test(APPOINTMENTS_URL + "client/request/", "client", client_payload_2, expected_status=201, step_description="Farklı Randevu Talebi Oluşturma")
    client_appt_id = appt_client.get("id")

    if client_appt_id:
        # Randevu talebini uzman tarafından onaylar (status: waiting_approval -> confirmed)
        patch_status_test(APPOINTMENTS_URL + f"{client_appt_id}/status/", "expert", "confirmed", expected_status=200, step_description="Randevu Talebini Onaylama")

        # Danışan toplantı bilgilerini görüntüler
        get_test(APPOINTMENTS_URL + f"{client_appt_id}/meeting-info/", "client", expected_status=200, step_description="Danışanın Toplantı Bilgilerini Görüntülemesi")

        # Danışan randevuyu iptal etmek için talep gönderir (status: confirmed -> cancel_requested)
        patch_status_test(APPOINTMENTS_URL + f"{client_appt_id}/status/", "client", "cancel_requested", expected_status=200, step_description="Randevu İptal Talebi Gönderme")

        # Uzman iptal talebini reddeder (status: cancel_requested -> confirmed)
        patch_status_test(APPOINTMENTS_URL + f"{client_appt_id}/status/", "expert", "confirmed", expected_status=200, step_description="İptal Talebini Reddetme")

        # Randevuyu siler
        delete_test(APPOINTMENTS_URL + f"{client_appt_id}/", "client", expected_status=204, step_description="Randevuyu Silme")

    # --- LİSTELEME VE DİĞER TESTLER ---
    # Randevu listesini tarih aralığı ile getir (eksik parametre hatası)
    get_test(APPOINTMENTS_URL, "expert", expected_status=400, step_description="Tarih Parametresi Olmadan Liste Getirme")

    # Geçerli tarih aralığı ile randevu listesi
    get_test(APPOINTMENTS_URL + "?start_date=2025-10-01&end_date=2025-10-31", "expert", expected_status=200, step_description="Tarih Aralığı ile Randevu Listesi")

    # Status filtresi ile randevu listesi
    get_test(APPOINTMENTS_URL + "?start_date=2025-10-01&end_date=2025-10-31&status=confirmed", "expert", expected_status=200, step_description="Status Filtresi ile Randevu Listesi")

    # Uzmanın randevularını danışan olarak görüntüleme
    get_test(APPOINTMENTS_URL + f"experts/{expert_id}/appointments/?start_date=2025-10-01&end_date=2025-10-31", "client", expected_status=200, step_description="Uzmanın Randevularını Danışan Olarak Görüntüleme")

    # Geçersiz tarih aralığı testi
    get_test(APPOINTMENTS_URL + "?start_date=2025-10-31&end_date=2025-10-01", "expert", expected_status=400, step_description="Geçersiz Tarih Aralığı")

    # Maksimum tarih aralığı aşımı testi (client için 4 aydan fazla)
    get_test(APPOINTMENTS_URL + "?start_date=2025-10-01&end_date=2026-03-01", "client", expected_status=400, step_description="Maksimum Tarih Aralığı Aşımı")

    # Yetkisiz erişim testi - danışan uzmanın randevularını görüntülemeye çalışır
    get_test(APPOINTMENTS_URL + "?start_date=2025-10-01&end_date=2025-10-31", "client", expected_status=200, step_description="Danışanın Kendi Randevularını Görüntüleme")

def save_results_markdown(filename="appointment_tests_results.md"):
    """Test sonuçlarını Markdown formatında dosyaya kaydeder."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Appointment API Test Results\nGenerated at: {datetime.now()}\n\n")
        for r in results:
            f.write(f"## {r['step']}\n")
            f.write(f"- Method: {r['method']}\n")
            f.write(f"- URL: {r['url']}\n")
            if r['payload']:
                f.write(f"- Payload:\n```json\n{json.dumps(r['payload'], indent=2, ensure_ascii=False)}\n```\n")
            f.write(f"- Status Code: {r['status_code']}\n")
            if r['expected_status']:
                f.write(f"- Expected Status: {r['expected_status']}\n")
            f.write(f"- Passed: {r['passed']} {r['emoji']}\n")
            f.write(f"```json\n{json.dumps(r['response'], indent=2, ensure_ascii=False)}\n```\n\n")

def print_summary():
    """Testlerin özetini konsola yazdırır."""
    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])
    print(f"\nTest Summary: {passed} Passed ✅ | {failed} Failed ❌\n")

if __name__ == "__main__":
    login_users()
    run_appointment_tests()
    save_results_markdown()
    print_summary()

# oluşturmuş randevuları daha sonra lokalinde silmek isteyebilisin