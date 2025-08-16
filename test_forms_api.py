#!/usr/bin/env python3
"""
Forms API Test Script
Bu script forms API endpoint'lerini test eder.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1/forms"

# Test data
SAMPLE_FORM_SUBMIT = {
    "form_id": 1,
    "answers": [
        {
            "question_id": 1,
            "text_answer": "Test: Baş ağrısı ve mide bulantısı yaşıyorum"
        },
        {
            "question_id": 2,
            "selected_option_ids": [3]
        },
        {
            "question_id": 3,
            "selected_option_ids": [6, 9, 10]
        },
        {
            "question_id": 4,
            "text_answer": "Test: Evet, 2 yıl önce benzer şikayetlerim vardı."
        }
    ]
}

def test_without_auth():
    """Authentication olmadan endpoint'leri test et"""
    print("🔒 Authentication olmadan test ediliyor...")
    
    # Forms list
    response = requests.get(f"{API_BASE}/")
    print(f"GET {API_BASE}/ - Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Authentication gerekli - beklenen davranış")
    else:
        print("❌ Authentication kontrolü çalışmıyor")
    
    print()

def test_with_auth(access_token):
    """Authentication ile endpoint'leri test et"""
    print("🔑 Authentication ile test ediliyor...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Forms list
    print(f"GET {API_BASE}/")
    response = requests.get(f"{API_BASE}/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        forms = response.json()
        print(f"✅ {len(forms)} form bulundu")
        for form in forms:
            print(f"  - {form['title']} (ID: {form['id']})")
    else:
        print(f"❌ Hata: {response.text}")
    print()
    
    # Form detail
    print(f"GET {API_BASE}/1/")
    response = requests.get(f"{API_BASE}/1/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        form = response.json()
        print(f"✅ Form: {form['title']}")
        print(f"  Soru sayısı: {len(form['questions'])}")
        print(f"  Daha önce dolduruldu mu: {form['has_responded']}")
        
        for question in form['questions']:
            print(f"  - {question['question_text'][:50]}... ({question['question_type']})")
    else:
        print(f"❌ Hata: {response.text}")
    print()
    
    # Submit form
    print(f"POST {API_BASE}/submit/")
    response = requests.post(
        f"{API_BASE}/submit/", 
        headers={**headers, "Content-Type": "application/json"},
        json=SAMPLE_FORM_SUBMIT
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Form başarıyla gönderildi: {result['message']}")
        print(f"  Response ID: {result['response_id']}")
    else:
        print(f"❌ Hata: {response.text}")
    print()
    
    # User responses
    print(f"GET {API_BASE}/my-responses/")
    response = requests.get(f"{API_BASE}/my-responses/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        responses = response.json()
        print(f"✅ {len(responses)} form cevabı bulundu")
        for resp in responses:
            print(f"  - {resp['form']['title']} - {resp['submitted_at']}")
    else:
        print(f"❌ Hata: {response.text}")
    print()

def main():
    """Ana test fonksiyonu"""
    print("🚀 Forms API Test Script")
    print("=" * 50)
    
    # Test without authentication
    test_without_auth()
    
    # Test with authentication (token gerekli)
    print("🔑 Authentication token ile test etmek için:")
    print("1. Bir kullanıcı ile giriş yapın")
    print("2. JWT token alın")
    print("3. Aşağıdaki fonksiyonu çağırın:")
    print("   test_with_auth('your_jwt_token_here')")
    print()
    
    # Eğer token varsa test et
    access_token = input("JWT token girin (boş bırakılırsa sadece auth test edilir): ").strip()
    if access_token:
        test_with_auth(access_token)
    
    print("✅ Test tamamlandı!")

if __name__ == "__main__":
    main()
