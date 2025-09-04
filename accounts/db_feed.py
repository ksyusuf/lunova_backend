#!/usr/bin/env python
"""
Database seeding script for accounts app
Run this script after migrations to populate initial data
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunova_backend.settings')
django.setup()

from accounts.models import Service, AddictionType, Gender


def seed_services():
    """Seed Service table with initial services"""
    services_data = [
        {"name": "Bilişsel Terapi", "description": "Bilişsel davranışçı terapi yöntemleri."},
        {"name": "Aile Terapisi", "description": "Aile içi ilişkiler üzerine terapi."},
        {"name": "Çocuk ve Ergen", "description": "Çocuk ve ergenlere yönelik psikolojik danışmanlık."},
        {"name": "Diğer", "description": "Belirtilmeyen diğer terapi türleri."},
    ]
    
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data["name"],
            defaults={"description": service_data["description"]}
        )
        if created:
            print(f"✓ Service created: {service.name}")
        else:
            print(f"○ Service already exists: {service.name}")


def seed_addiction_types():
    """Seed AddictionType table with initial addiction types"""
    addiction_names = [
        "Alcohol",
        "Substance", 
        "Digital",
        "Gambling",
        "Other"
    ]
    
    for name in addiction_names:
        addiction_type, created = AddictionType.objects.get_or_create(name=name)
        if created:
            print(f"✓ AddictionType created: {addiction_type.name}")
        else:
            print(f"○ AddictionType already exists: {addiction_type.name}")


def seed_genders():
    """Seed Gender table with initial gender options"""
    gender_names = [
        "Kadın",
        "Erkek",
        "Diğer", 
        "Belirtmek istemiyorum"
    ]
    
    for name in gender_names:
        gender, created = Gender.objects.get_or_create(name=name)
        if created:
            print(f"✓ Gender created: {gender.name}")
        else:
            print(f"○ Gender already exists: {gender.name}")


def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    print("=" * 50)
    
    try:
        seed_services()
        print("-" * 30)
        seed_addiction_types()
        print("-" * 30)
        seed_genders()
        print("-" * 30)
        
        print("✅ Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
