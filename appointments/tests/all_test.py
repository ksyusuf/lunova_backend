import requests
import json
from datetime import datetime

"""
yapılan test sonrası tekrar çalıştırmak için lokalde oluşturulmuş
expert: 22
client: 21
randevularını silebilirsin.

# todo: bu testler yeniden yapılacak. çünkü endpoint yapısı değişti.

---
istek özeti

1.  **Login expert**: Uzman kullanıcının sisteme giriş yaparak bir erişim tokenı almasını sağlar.
2.  **Login client**: Danışan kullanıcının sisteme giriş yaparak bir erişim tokenı almasını sağlar.
3.  **expert POST create**: Uzmanın, danışan için bir randevu oluşturmasını test eder.
4.  **expert POST create**: Aynı randevuyu tekrar oluşturarak çakışma hatası (`400`) almayı test eder.
5.  **expert POST create**: Yeni ve geçerli bir randevu oluşturur.
6.  **expert POST approve**: Zaten onay beklemeyen bir randevuyu onaylama yetkisini test eder ve hata alır.
7.  **expert POST confirm**: Bir randevuyu uzman tarafından onaylar.
8.  **expert POST cancel-request**: Uzmanın randevu için iptal talebi oluşturma yetkisinin olmadığını (`403`) test eder.
9.  **expert POST cancel-confirm**: İptal talebi olmayan bir randevuyu iptal etmeye çalışır.
10. **expert DELETE**: Belirtilen randevuyu başarıyla siler.
11. **client POST request**: Danışanın, uzman için bir randevu talebi oluşturmasını test eder.
12. **client POST request**: Aynı randevu talebini tekrar oluşturarak çakışma hatası (`400`) almayı test eder.
13. **expert POST request**: Uzmanın, sadece danışanlara açık olan randevu talep endpoint'ini kullanma yetkisinin olmadığını (`403`) test eder.
14. **client POST request**: Yeni ve geçerli bir randevu talebi oluşturur.
15. **expert POST approve**: Danışandan gelen randevu talebini uzman tarafından onaylar.
16. **expert POST confirm**: Onaylanmış randevuyu tekrar onaylayarak endpoint'in idempotent (tekrar çalıştırılabilir) olup olmadığını kontrol eder.
17. **client GET meeting-info**: Danışanın, onaylanmış randevunun toplantı bilgilerini görüntüleyebildiğini test eder.
18. **client POST cancel-request**: Danışanın, randevu için iptal talebi oluşturmasını test eder.
19. **client POST cancel-confirm**: Danışanın, kendi gönderdiği iptal talebini onaylama yetkisinin olmadığını (`403`) test eder.
20. **client DELETE**: Belirtilen randevuyu başarıyla siler.
"""

BASE_URL = "http://127.0.0.1:8000/api/v1/"
APPOINTMENTS_URL = BASE_URL + "appointments/"
LOGIN_URL = BASE_URL + "accounts/login/"

USERS = {
    "expert": {"email": "ozel_@expert.com", "password": "yusuf123"},
    "client": {"email": "ozel_@client.com", "password": "yusuf123"}
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

def run_appointment_tests():
    """Randevu API'si için tüm test senaryolarını çalıştırır."""
    expert_id = 21
    client_id = 22

    # --- EXPERT AKIŞI ---
    # Uzman randevu oluşturur (başarılı senaryo)
    expert_payload_1 = {"expert": expert_id, "client": client_id, "date": "2025-08-20", "time": "14:00:00", "duration": 60}
    post_test(APPOINTMENTS_URL + "expert/create/", "expert", expert_payload_1, expected_status=201, step_description="Randevu Oluşturma (başarılı)")

    # Aynı randevuyu tekrar oluşturma girişimi (hata senaryosu)
    post_test(APPOINTMENTS_URL + "expert/create/", "expert", expert_payload_1, expected_status=400, step_description="Aynı Randevuyu Tekrar Oluşturma")

    # Yeni bir randevu oluşturur
    expert_payload_2 = {"expert": expert_id, "client": client_id, "date": "2025-08-21", "time": "10:00:00", "duration": 45}
    appt = post_test(APPOINTMENTS_URL + "expert/create/", "expert", expert_payload_2, expected_status=201, step_description="Farklı Randevu Oluşturma")
    expert_appt_id = appt.get("id")

    if expert_appt_id:
        # Zaten onay beklemeyen bir randevuyu onaylamaya çalışma girişimi (hata senaryosu)
        post_test(APPOINTMENTS_URL + f"{expert_appt_id}/approve/", "expert", expected_status=400, step_description="Onaylanmamış Randevuyu Onaylama Girişimi")

        # Randevuyu onaylar
        post_test(APPOINTMENTS_URL + f"{expert_appt_id}/confirm/", "expert", expected_status=200, step_description="Randevuyu Onaylama")

        # Uzmanın iptal talebi oluşturma yetkisini kontrol eder (hata senaryosu)
        post_test(APPOINTMENTS_URL + f"{expert_appt_id}/cancel-request/", "expert", expected_status=403, step_description="Uzmanın İptal Talebi Oluşturma Girişimi")

        # İptal talebi olmayan bir randevuyu iptal etme girişimi (hata senaryosu)
        post_test(APPOINTMENTS_URL + f"{expert_appt_id}/cancel-confirm/", "expert", json_data={"confirm": True}, expected_status=400, step_description="İptal Talebi Olmayan Randevuyu İptal Etme")

        # Randevuyu siler
        delete_test(APPOINTMENTS_URL + f"{expert_appt_id}/", "expert", expected_status=204, step_description="Randevuyu Silme")

    # --- CLIENT AKIŞI ---
    # Danışan randevu talebi oluşturur (başarılı senaryo)
    client_payload_1 = {"expert": expert_id, "date": "2025-08-22", "time": "11:00:00", "duration": 30}
    post_test(APPOINTMENTS_URL + "client/request/", "client", client_payload_1, expected_status=201, step_description="Randevu Talebi Oluşturma (başarılı)")

    # Aynı randevu talebini tekrar oluşturma girişimi (hata senaryosu)
    post_test(APPOINTMENTS_URL + "client/request/", "client", client_payload_1, expected_status=400, step_description="Aynı Randevu Talebini Tekrar Oluşturma")

    # Uzmanın danışan endpoint'ini kullanma yetkisini kontrol eder (hata senaryosu)
    post_test(APPOINTMENTS_URL + "client/request/", "expert", client_payload_1, expected_status=403, step_description="Uzmanın Danışan Endpoint'ini Kullanma Girişimi")

    # Farklı bir randevu talebi oluşturur
    client_payload_2 = {"expert": expert_id, "date": "2025-08-23", "time": "12:00:00", "duration": 60}
    appt_client = post_test(APPOINTMENTS_URL + "client/request/", "client", client_payload_2, expected_status=201, step_description="Farklı Randevu Talebi Oluşturma")
    client_appt_id = appt_client.get("id")

    if client_appt_id:
        # Randevu talebini uzman tarafından onaylar
        post_test(APPOINTMENTS_URL + f"{client_appt_id}/approve/", "expert", expected_status=200, step_description="Randevu Talebini Onaylama")

        # Onaylanmış randevuyu tekrar onaylar (idempotent kontrolü)
        post_test(APPOINTMENTS_URL + f"{client_appt_id}/confirm/", "expert", expected_status=200, step_description="Onaylanmış Randevuyu Tekrar Onaylama")

        # Danışan toplantı bilgilerini görüntüler
        get_test(APPOINTMENTS_URL + f"{client_appt_id}/meeting-info/", "client", expected_status=200, step_description="Danışanın Toplantı Bilgilerini Görüntülemesi")

        # Danışan randevuyu iptal etmek için talep gönderir
        post_test(APPOINTMENTS_URL + f"{client_appt_id}/cancel-request/", "client", expected_status=200, step_description="Randevu İptal Talebi Gönderme")

        # Danışanın iptal talebini onaylama yetkisini kontrol eder (hata senaryosu)
        post_test(APPOINTMENTS_URL + f"{client_appt_id}/cancel-confirm/", "client", json_data={"confirm": True}, expected_status=403, step_description="Danışanın İptal Talebini Onaylama Girişimi")

        # Randevuyu siler
        delete_test(APPOINTMENTS_URL + f"{client_appt_id}/", "client", expected_status=204, step_description="Randevuyu Silme")

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