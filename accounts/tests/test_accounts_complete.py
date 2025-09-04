#!/usr/bin/env python3
"""
Sadeleştirilmiş Hesaplar API Test Süiti

Kullanıcı kaydı, giriş ve çıkış temel akışlarını test eder.
- Kayıt (Expert, Client, Admin)
- Mükerrer kayıt hataları (parola uyuşmazlığı, eksik alan)
- Giriş
- Çıkış
"""

import requests
import os
import time
import random
import string
from typing import Dict, Any, Optional

class SimplifiedAccountsTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def generate_random_string(self, length: int = 8) -> str:
        """Benzersiz test verileri için rastgele dize oluşturur."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def generate_random_email(self, role: str = "test") -> str:
        """Test için benzersiz e-posta oluşturur."""
        timestamp = int(time.time())
        random_str = self.generate_random_string(4)
        return f"{role}_{random_str}_{timestamp}@test.com"
    
    def generate_random_phone(self) -> str:
        """Rastgele bir Türk telefon numarası oluşturur."""
        return f"053{random.randint(10000000, 99999999)}"
    
    def generate_random_tc(self) -> str:
        """Rastgele bir Türk kimlik numarası oluşturur."""
        return str(random.randint(10000000000, 99999999999))
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Test sonuçlarını kaydeder ve ekrana basar."""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test_name": test_name,
            "success": success,
            "details": details
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {details}")

    def test_registration(self, role: str, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Genel kayıt testini gerçekleştirir."""
        test_name = f"Valid {role.capitalize()} Registration"
        try:
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                user_data = response.json()
                self.log_test(test_name, True, f"User created with ID: {user_data.get('id')}")
                return {
                    "role": role,
                    "email": data["email"],
                    "password": data["password"],
                    "user_id": user_data.get("id")
                }
            else:
                self.log_test(test_name, False, f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
            return None

    def test_invalid_registration(self):
        """Çeşitli geçersiz kayıt senaryolarını test eder."""
        print("\n❌ Testing Invalid Registration Scenarios...")
        
        invalid_cases = [
            {
                "name": "Password Mismatch",
                "endpoint": "/api/v1/accounts/register/expert/",
                "data": {
                    "first_name": "Test", "last_name": "User", "email": self.generate_random_email("invalid"),
                    "password": "Test123!", "password2": "Different123!", "phone_number": self.generate_random_phone(),
                    "id_number": self.generate_random_tc(), "country": "TR", "university": "Test University"
                }
            },
            {
                "name": "Missing Required Fields",
                "endpoint": "/api/v1/accounts/register/client/",
                "data": {
                    "first_name": "Test", "email": self.generate_random_email("incomplete"), "password": "Test123!"
                }
            },
            {
                "name": "Invalid Email Format",
                "endpoint": "/api/v1/accounts/register/expert/",
                "data": {
                    "first_name": "Test", "last_name": "User", "email": "invalid-email",
                    "password": "Test123!", "password2": "Test123!", "phone_number": self.generate_random_phone(),
                    "id_number": self.generate_random_tc(), "country": "TR", "university": "Test University"
                }
            },
            {
                "name": "Expert Missing TC (TR)",
                "endpoint": "/api/v1/accounts/register/expert/",
                "data": {
                    "first_name": "Exp", "last_name": "User", "email": self.generate_random_email("expert_no_tc"),
                    "password": "Test123!", "password2": "Test123!", "phone_number": self.generate_random_phone(),
                    "country": "TR", "university": "Test University"
                }
            },
            {
                "name": "Expert Missing University",
                "endpoint": "/api/v1/accounts/register/expert/",
                "data": {
                    "first_name": "Exp", "last_name": "User", "email": self.generate_random_email("expert_no_uni"),
                    "password": "Test123!", "password2": "Test123!", "phone_number": self.generate_random_phone(),
                    "id_number": self.generate_random_tc(), "country": "TR"
                }
            },
            {
                "name": "Client Invalid Email Format",
                "endpoint": "/api/v1/accounts/register/client/",
                "data": {
                    "first_name": "Cli", "last_name": "User", "email": "not-an-email",
                    "password": "Test123!", "password2": "Test123!", "phone_number": self.generate_random_phone(),
                    "id_number": self.generate_random_tc(), "country": "TR"
                }
            },
            {
                "name": "Admin Invalid Email Format",
                "endpoint": "/api/v1/accounts/register/admin/",
                "data": {
                    "first_name": "Adm", "last_name": "User", "email": "invalid@",
                    "password": "Test123!", "password2": "Test123!", "phone_number": self.generate_random_phone(),
                    "id_number": self.generate_random_tc(), "country": "TR"
                }
            },
            {
                "name": "Client Missing Phone Number",
                "endpoint": "/api/v1/accounts/register/client/",
                "data": {
                    "first_name": "Cli", "last_name": "User", "email": self.generate_random_email("client_no_phone"),
                    "password": "Test123!", "password2": "Test123!",
                    "id_number": self.generate_random_tc(), "country": "TR"
                }
            },
            {
                "name": "Admin Missing Last Name",
                "endpoint": "/api/v1/accounts/register/admin/",
                "data": {
                    "first_name": "Adm", "last_name": "", "email": self.generate_random_email("admin_no_last"),
                    "password": "Test123!", "password2": "Test123!", "phone_number": self.generate_random_phone(),
                    "id_number": self.generate_random_tc(), "country": "TR"
                }
            },
            {
                "name": "Client Invalid TCKN Length",
                "endpoint": "/api/v1/accounts/register/client/",
                "data": {
                    "first_name": "Cli", "last_name": "User", "email": self.generate_random_email("client_bad_tc"),
                    "password": "Test123!", "password2": "Test123!", "phone_number": self.generate_random_phone(),
                    "id_number": "1234567890", "country": "TR"
                }
            },
            {
                "name": "Client Non-digit TCKN",
                "endpoint": "/api/v1/accounts/register/client/",
                "data": {
                    "first_name": "Cli", "last_name": "User", "email": self.generate_random_email("client_non_digit_tc"),
                    "password": "Test123!", "password2": "Test123!", "phone_number": self.generate_random_phone(),
                    "id_number": "12345abcde1", "country": "TR"
                }
            }
        ]
        
        for case in invalid_cases:
            try:
                response = self.session.post(
                    f"{self.base_url}{case['endpoint']}",
                    json=case["data"],
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [400, 422]:
                    self.log_test(case["name"], True, f"Properly rejected with status: {response.status_code}")
                else:
                    self.log_test(case["name"], False, f"Should have failed but got status: {response.status_code}")
            except Exception as e:
                self.log_test(case["name"], False, f"Exception: {str(e)}")

    def test_login(self, user_data: Dict[str, Any], is_valid: bool = True) -> bool:
        """Kullanıcı girişini test eder ve refresh token'ı çerez olarak saklar."""
        test_name = f"Login for {user_data['role']}" if is_valid else f"Invalid Login for {user_data['role']}"
        try:
            data = {"email": user_data["email"], "password": user_data["password"]}
            if not is_valid:
                data["password"] = "wrong_password"

            response = self.session.post(
                f"{self.base_url}/api/v1/accounts/login/",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if is_valid and response.status_code == 200:
                login_data = response.json()
                user_data["token"] = login_data.get("access")
                
                # REFRESH TOKEN'I ÇEREZ OLARAK SAKLA
                if "refresh" in login_data:
                    self.session.cookies.set("refresh_token", login_data.get("refresh"))
                
                self.log_test(test_name, True, "Login successful")
                return True
            elif not is_valid and response.status_code in [400, 401, 403]:
                self.log_test(test_name, True, f"Properly rejected with status: {response.status_code}")
                return False
            else:
                self.log_test(test_name, False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
            return False

    def test_logout(self, user_data: Dict[str, Any]) -> bool:
        """Kullanıcı çıkışını test eder."""
        test_name = f"Logout for {user_data['role']}"
        if not user_data.get("token"):
            self.log_test(test_name, False, "No token available to logout")
            return False
        
        try:
            # requests.Session, bir önceki testte set edilen çerezi otomatik olarak gönderir
            headers = {"Authorization": f"Bearer {user_data['token']}"}
            response = self.session.post(
                f"{self.base_url}/api/v1/accounts/logout/",
                headers=headers
            )
            
            if response.status_code in [200, 205]:
                self.log_test(test_name, True, "Logout successful")
                return True
            else:
                self.log_test(test_name, False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Tüm test senaryolarını çalıştırır."""
        print("🚀 Starting Simplified Accounts API Test Suite...")
        print("=" * 60)

        expert_user = self.test_registration(
            "expert",
            "/api/v1/accounts/register/expert/",
            {
                "first_name": "Dr. Ahmet", "last_name": "Uzman", "email": self.generate_random_email("expert"),
                "password": "Test123!", "password2": "Test123!", "phone_number": "05311234567",
                "id_number": self.generate_random_tc(), "country": "TR", "university": "İstanbul Üniversitesi",
                "about": "Uzman psikolog"
            }
        )
        if expert_user:
            self.test_login(expert_user)
            # Yanlış şifre ile giriş
            self.test_login(expert_user, is_valid=False)
            self.test_logout(expert_user)

        # Client kullanıcısı kaydı ve yanlış şifre ile giriş testi
        client_user = self.test_registration(
            "client",
            "/api/v1/accounts/register/client/",
            {
                "first_name": "Ali", "last_name": "Danışan", "email": self.generate_random_email("client"),
                "password": "Test123!", "password2": "Test123!", "phone_number": self.generate_random_phone(),
                "id_number": self.generate_random_tc(), "country": "TR"
            }
        )
        if client_user:
            # Yanlış şifre ile giriş
            self.test_login(client_user, is_valid=False)

        # Admin kullanıcısı kaydı ve yanlış şifre ile giriş testi
        admin_user = self.test_registration(
            "admin",
            "/api/v1/accounts/register/admin/",
            {
                "first_name": "Ayşe", "last_name": "Yönetici", "email": self.generate_random_email("admin"),
                "password": "Test123!", "password2": "Test123!", "phone_number": self.generate_random_phone(),
                "id_number": self.generate_random_tc(), "country": "TR"
            }
        )
        if admin_user:
            # Yanlış şifre ile giriş
            self.test_login(admin_user, is_valid=False)

        self.test_invalid_registration()

        self.print_test_summary()
    
    def print_test_summary(self):
        """Test sonuçlarının özetini ekrana basar."""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        if total_tests > 0:
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['details']}")

def main():
    """Ana fonksiyon."""
    environment = os.environ.get("ENVIRONMENT", "Development")
    debug = os.environ.get("DEBUG", "False").lower() in ("1", "true", "yes")

    if environment != "Development" and not debug:
        print("⚠️ Tests are restricted to development mode. Set ENVIRONMENT=Development or DEBUG=true to run.")
        return

    tester = SimplifiedAccountsTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()