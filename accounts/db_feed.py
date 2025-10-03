#!/usr/bin/env python
"""
Database seeding script for accounts app
Run this script after migrations to populate initial data
"""

import os
import sys
import django
import random
from datetime import date, timedelta
from django.utils.text import slugify

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunova_backend.settings')
django.setup()

from accounts.models import Service, AddictionType, Gender, User, ExpertProfile, ClientProfile, UserRole

# Sample data for profiles
TURKISH_FIRST_NAMES = [
    "Ahmet", "Mehmet", "Ayşe", "Fatma", "Ali", "Mustafa", "Emine", "Hüseyin",
    "Hatice", "İbrahim", "Zeynep", "Hasan", "Elif", "Osman", "Halime",
    "Ayşe", "Fatma", "Emine", "Hatice", "Zeynep", "Elif", "Halime"
]

ENGLISH_FIRST_NAMES = [
    "John", "Jane", "Michael", "Sarah", "David", "Emma", "James", "Olivia",
    "Robert", "Sophia", "William", "Isabella", "Joseph", "Ava", "Charles",
    "Mia", "Thomas", "Charlotte", "Christopher", "Amelia"
]

SURNAMES = [
    "Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Öztürk", "Aydın",
    "Kılıç", "Arslan", "Smith", "Johnson", "Williams", "Brown", "Jones",
    "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor"
]

UNIVERSITIES = [
    "İstanbul Üniversitesi", "Ankara Üniversitesi", "Ege Üniversitesi",
    "Hacettepe Üniversitesi", "ODTÜ", "Boğaziçi Üniversitesi",
    "Harvard University", "Stanford University", "MIT", "Oxford University"
]

ABOUT_TEXTS = [
    "Uzman psikolog, bilişsel davranışçı terapi alanında deneyimli.",
    "Aile terapisi uzmanı, 10 yıllık deneyim.",
    "Çocuk ve ergen psikolojisi konusunda uzman.",
    "Bağımlılık tedavisi konusunda uzmanlaşmış terapist.",
    "Clinical psychologist with expertise in cognitive behavioral therapy.",
    "Family therapist with over 10 years of experience.",
    "Specialist in child and adolescent psychology.",
    "Addiction treatment specialist."
]

SUPPORT_GOALS = [
    "Bağımlılıktan kurtulmak ve sağlıklı bir yaşam sürdürmek.",
    "Aile içi sorunları çözmek.",
    "Stres yönetimi ve anksiyete ile başa çıkmak.",
    "İlişki sorunlarını çözmek.",
    "To overcome addiction and maintain a healthy lifestyle.",
    "To resolve family issues.",
    "To manage stress and cope with anxiety.",
    "To solve relationship problems."
]


def seed_services():
    """Seed Service table with initial services"""
    services_data = [
        {"name": "Bilişsel Terapi", "description": "Bilişsel davranışçı terapi yöntemleri."},
        {"name": "Aile Terapisi", "description": "Aile içi ilişkiler üzerine terapi."},
        {"name": "Çocuk ve Ergen", "description": "Çocuk ve ergenlere yönelik psikolojik danışmanlık."},
        {"name": "Diğer", "description": "Belirtilmeyen diğer terapi türleri."},
    ]

    for service_data in services_data:
        slug = slugify(service_data["name"])
        service, created = Service.objects.get_or_create(
            name=service_data["name"],
            defaults={
                "slug": slug,
                "description": service_data["description"]
            }
        )
        if created:
            print(f"✓ Service created: {service.name} (slug: {service.slug})")
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
        slug = slugify(name)
        addiction_type, created = AddictionType.objects.get_or_create(
            name=name,
            defaults={"slug": slug}
        )
        if created:
            print(f"✓ AddictionType created: {addiction_type.name} (slug: {addiction_type.slug})")
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


def seed_expert_profiles():
    """Seed ExpertProfile table with sample expert profiles"""
    services = list(Service.objects.all())
    genders = list(Gender.objects.all())

    for i in range(20):
        # Generate random name
        first_name_pool = TURKISH_FIRST_NAMES + ENGLISH_FIRST_NAMES
        surname_pool = SURNAMES
        first_name = random.choice(first_name_pool)
        last_name = random.choice(surname_pool)

        # Generate unique email
        email = f"expert{i+1}@example.com"

        # Generate random birth date (25-65 years old)
        today = date.today()
        birth_date = today - timedelta(days=random.randint(25*365, 65*365))

        # Generate random 11-digit ID number
        id_number = ''.join(random.choices('0123456789', k=11))

        # Create user
        user = User.objects.create_user(
            email=email,
            password='password123',  # Default password
            first_name=first_name,
            last_name=last_name,
            role=UserRole.EXPERT,
            birth_date=birth_date,
            gender=random.choice(genders),
            id_number=id_number,
            phone_number=f"+90{random.randint(5000000000, 5999999999)}"
        )

        # Create expert profile
        expert_profile = ExpertProfile.objects.create(
            user=user,
            university=random.choice(UNIVERSITIES),
            about=random.choice(ABOUT_TEXTS),
            approval_status=random.choice([True, False])
        )

        # Assign random services (1-3 services)
        num_services = random.randint(1, 3)
        selected_services = random.sample(services, num_services)
        expert_profile.services.set(selected_services)

        print(f"✓ Expert profile created: {user.get_full_name()} ({email})")


def seed_client_profiles():
    """Seed ClientProfile table with sample client profiles"""
    addiction_types = list(AddictionType.objects.all())
    genders = list(Gender.objects.all())

    for i in range(100):
        # Generate random name
        first_name_pool = TURKISH_FIRST_NAMES + ENGLISH_FIRST_NAMES
        surname_pool = SURNAMES
        first_name = random.choice(first_name_pool)
        last_name = random.choice(surname_pool)

        # Generate unique email
        email = f"client{i+1}@example.com"

        # Generate random birth date (18-70 years old)
        today = date.today()
        birth_date = today - timedelta(days=random.randint(18*365, 70*365))

        # Generate random 11-digit ID number
        id_number = ''.join(random.choices('0123456789', k=11))

        # Create user
        user = User.objects.create_user(
            email=email,
            password='password123',  # Default password
            first_name=first_name,
            last_name=last_name,
            role=UserRole.CLIENT,
            birth_date=birth_date,
            gender=random.choice(genders),
            id_number=id_number,
            phone_number=f"+90{random.randint(5000000000, 5999999999)}"
        )

        # Create client profile
        client_profile = ClientProfile.objects.create(
            user=user,
            received_service_before=random.choice([True, False]),
            support_goal=random.choice(SUPPORT_GOALS)
        )

        # Assign random substances (0-2 addiction types)
        num_substances = random.randint(0, 2)
        if num_substances > 0 and addiction_types:
            selected_substances = random.sample(addiction_types, num_substances)
            client_profile.substances_used.set(selected_substances)

        print(f"✓ Client profile created: {user.get_full_name()} ({email})")


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
        seed_expert_profiles()
        print("-" * 30)
        seed_client_profiles()
        print("-" * 30)

        print("✅ Database seeding completed successfully!")

    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
