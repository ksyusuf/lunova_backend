"""
Database seeding script for appointments app
Run this script after migrations to populate initial appointment data
"""

import os
import sys
import django

# Script nereden çalıştırılırsa çalışsın, proje kökünü bul
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # script dizini
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))  # 2 seviye yukarı backend
sys.path.insert(0, BACKEND_DIR)

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunova_backend.settings')  # settings.py konumuna göre değiştir
django.setup()

import random
from datetime import date, time, datetime, timedelta
from appointments.models import Appointment
from accounts.models import User, UserRole

# Sample appointment notes
APPOINTMENT_NOTES = [
    "İlk görüşme - tanı değerlendirmesi",
    "Düzenli terapi seansı",
    "Aile terapisi oturumu",
    "Kriz müdahalesi",
    "İlerleme değerlendirmesi",
    "Son seans - bitirme görüşmesi",
    "Acil durum görüşmesi",
    "Online terapi seansı",
    "Grup terapisi hazırlığı",
    "İlaç tedavisi değerlendirmesi",
    "First consultation - diagnostic assessment",
    "Regular therapy session",
    "Family therapy session",
    "Crisis intervention",
    "Progress evaluation",
    "Final session - termination interview",
    "Emergency consultation",
    "Online therapy session",
    "Group therapy preparation",
    "Medication evaluation"
]

# Time slots for appointments (9 AM to 6 PM)
TIME_SLOTS = [
    time(9, 0), time(9, 30), time(10, 0), time(10, 30), time(11, 0), time(11, 30),
    time(12, 0), time(12, 30), time(13, 0), time(13, 30), time(14, 0), time(14, 30),
    time(15, 0), time(15, 30), time(16, 0), time(16, 30), time(17, 0), time(17, 30)
]


def get_experts_and_clients():
    """Get all experts and clients from database"""
    experts = list(User.objects.filter(role=UserRole.EXPERT))
    clients = list(User.objects.filter(role=UserRole.CLIENT))

    if not experts:
        print("❌ No experts found. Please run accounts db_feed.py first.")
        sys.exit(1)

    if not clients:
        print("❌ No clients found. Please run accounts db_feed.py first.")
        sys.exit(1)

    return experts, clients


def generate_random_date():
    """Generate a random date within the next 6 months"""
    today = date.today()
    max_date = today + timedelta(days=180)  # 6 months
    random_days = random.randint(0, 180)
    return today + timedelta(days=random_days)


def generate_zoom_data():
    """Generate mock Zoom meeting data"""
    meeting_id = f"zoom_{random.randint(100000000, 999999999)}"
    return {
        'zoom_meeting_id': meeting_id,
        'zoom_start_url': f"https://zoom.us/s/{meeting_id}",
        'zoom_join_url': f"https://zoom.us/j/{meeting_id}"
    }


def seed_pending_appointments(experts, clients, count=40):
    """Seed appointments with 'pending' status (expert created, waiting for confirmation)"""
    print(f"🌱 Seeding {count} pending appointments...")

    for i in range(count):
        expert = random.choice(experts)
        client = random.choice(clients)

        # Ensure no duplicate appointments for same expert-client-date-time
        while True:
            appointment_date = generate_random_date()
            appointment_time = random.choice(TIME_SLOTS)

            existing = Appointment.objects.filter(
                expert=expert,
                client=client,
                date=appointment_date,
                time=appointment_time
            ).exists()

            if not existing:
                break

        appointment = Appointment.objects.create(
            expert=expert,
            client=client,
            date=appointment_date,
            time=appointment_time,
            duration=random.choice([30, 45, 60]),
            status='pending',
            is_confirmed=False,
            notes=random.choice(APPOINTMENT_NOTES) if random.random() > 0.3 else ""
        )

        print(f"✓ Pending appointment created: {expert.get_full_name()} ↔ {client.get_full_name()} ({appointment_date})")


def seed_waiting_approval_appointments(experts, clients, count=40):
    """Seed appointments with 'waiting_approval' status (client requested)"""
    print(f"🌱 Seeding {count} waiting approval appointments...")

    for i in range(count):
        expert = random.choice(experts)
        client = random.choice(clients)

        # Ensure no duplicate appointments for same expert-client-date-time
        while True:
            appointment_date = generate_random_date()
            appointment_time = random.choice(TIME_SLOTS)

            existing = Appointment.objects.filter(
                expert=expert,
                client=client,
                date=appointment_date,
                time=appointment_time
            ).exists()

            if not existing:
                break

        appointment = Appointment.objects.create(
            expert=expert,
            client=client,
            date=appointment_date,
            time=appointment_time,
            duration=random.choice([30, 45, 60]),
            status='waiting_approval',
            is_confirmed=False,
            notes=random.choice(APPOINTMENT_NOTES) if random.random() > 0.3 else ""
        )

        print(f"✓ Waiting approval appointment created: {expert.get_full_name()} ↔ {client.get_full_name()} ({appointment_date})")


def seed_confirmed_appointments(experts, clients, count=60):
    """Seed appointments with 'confirmed' status"""
    print(f"🌱 Seeding {count} confirmed appointments...")

    for i in range(count):
        expert = random.choice(experts)
        client = random.choice(clients)

        # Ensure no duplicate appointments for same expert-client-date-time
        while True:
            appointment_date = generate_random_date()
            appointment_time = random.choice(TIME_SLOTS)

            existing = Appointment.objects.filter(
                expert=expert,
                client=client,
                date=appointment_date,
                time=appointment_time
            ).exists()

            if not existing:
                break

        # Some confirmed appointments have Zoom data
        zoom_data = {}
        if random.random() > 0.4:  # 60% chance of having Zoom data
            zoom_data = generate_zoom_data()

        appointment = Appointment.objects.create(
            expert=expert,
            client=client,
            date=appointment_date,
            time=appointment_time,
            duration=random.choice([30, 45, 60]),
            status='confirmed',
            is_confirmed=True,
            notes=random.choice(APPOINTMENT_NOTES) if random.random() > 0.3 else "",
            **zoom_data
        )

        zoom_status = "with Zoom" if zoom_data else "without Zoom"
        print(f"✓ Confirmed appointment created: {expert.get_full_name()} ↔ {client.get_full_name()} ({appointment_date}) {zoom_status}")


def seed_cancel_requested_appointments(experts, clients, count=20):
    """Seed appointments with 'cancel_requested' status"""
    print(f"🌱 Seeding {count} cancel requested appointments...")

    for i in range(count):
        expert = random.choice(experts)
        client = random.choice(clients)

        # Ensure no duplicate appointments for same expert-client-date-time
        while True:
            appointment_date = generate_random_date()
            appointment_time = random.choice(TIME_SLOTS)

            existing = Appointment.objects.filter(
                expert=expert,
                client=client,
                date=appointment_date,
                time=appointment_time
            ).exists()

            if not existing:
                break

        appointment = Appointment.objects.create(
            expert=expert,
            client=client,
            date=appointment_date,
            time=appointment_time,
            duration=random.choice([30, 45, 60]),
            status='cancel_requested',
            is_confirmed=True,
            notes=random.choice(APPOINTMENT_NOTES) if random.random() > 0.3 else ""
        )

        print(f"✓ Cancel requested appointment created: {expert.get_full_name()} ↔ {client.get_full_name()} ({appointment_date})")


def seed_cancelled_appointments(experts, clients, count=20):
    """Seed appointments with 'cancelled' status"""
    print(f"🌱 Seeding {count} cancelled appointments...")

    for i in range(count):
        expert = random.choice(experts)
        client = random.choice(clients)

        # Ensure no duplicate appointments for same expert-client-date-time
        while True:
            appointment_date = generate_random_date()
            appointment_time = random.choice(TIME_SLOTS)

            existing = Appointment.objects.filter(
                expert=expert,
                client=client,
                date=appointment_date,
                time=appointment_time
            ).exists()

            if not existing:
                break

        appointment = Appointment.objects.create(
            expert=expert,
            client=client,
            date=appointment_date,
            time=appointment_time,
            duration=random.choice([30, 45, 60]),
            status='cancelled',
            is_confirmed=False,
            notes=random.choice(APPOINTMENT_NOTES) if random.random() > 0.3 else ""
        )

        print(f"✓ Cancelled appointment created: {expert.get_full_name()} ↔ {client.get_full_name()} ({appointment_date})")


def seed_completed_appointments(experts, clients, count=20):
    """Seed appointments with 'completed' status (past dates)"""
    print(f"🌱 Seeding {count} completed appointments...")

    for i in range(count):
        expert = random.choice(experts)
        client = random.choice(clients)

        # Ensure no duplicate appointments for same expert-client-date-time
        while True:
            # Past dates for completed appointments
            today = date.today()
            past_days = random.randint(1, 90)  # Within last 3 months
            appointment_date = today - timedelta(days=past_days)
            appointment_time = random.choice(TIME_SLOTS)

            existing = Appointment.objects.filter(
                expert=expert,
                client=client,
                date=appointment_date,
                time=appointment_time
            ).exists()

            if not existing:
                break

        # Some completed appointments have Zoom data
        zoom_data = {}
        if random.random() > 0.3:  # 70% chance of having Zoom data for completed appointments
            zoom_data = generate_zoom_data()

        appointment = Appointment.objects.create(
            expert=expert,
            client=client,
            date=appointment_date,
            time=appointment_time,
            duration=random.choice([30, 45, 60]),
            status='completed',
            is_confirmed=True,
            notes=random.choice(APPOINTMENT_NOTES) if random.random() > 0.3 else "",
            **zoom_data
        )

        zoom_status = "with Zoom" if zoom_data else "without Zoom"
        print(f"✓ Completed appointment created: {expert.get_full_name()} ↔ {client.get_full_name()} ({appointment_date}) {zoom_status}")


def seed_soft_deleted_appointments(experts, clients, count=10):
    """Seed soft deleted appointments"""
    print(f"🌱 Seeding {count} soft deleted appointments...")

    for i in range(count):
        expert = random.choice(experts)
        client = random.choice(clients)

        # Ensure no duplicate appointments for same expert-client-date-time
        while True:
            appointment_date = generate_random_date()
            appointment_time = random.choice(TIME_SLOTS)

            existing = Appointment.objects.filter(
                expert=expert,
                client=client,
                date=appointment_date,
                time=appointment_time
            ).exists()

            if not existing:
                break

        appointment = Appointment.objects.create(
            expert=expert,
            client=client,
            date=appointment_date,
            time=appointment_time,
            duration=random.choice([30, 45, 60]),
            status=random.choice(['pending', 'confirmed', 'cancelled']),
            is_confirmed=random.choice([True, False]),
            is_deleted=True,
            notes=random.choice(APPOINTMENT_NOTES) if random.random() > 0.3 else ""
        )

        print(f"✓ Soft deleted appointment created: {expert.get_full_name()} ↔ {client.get_full_name()} ({appointment_date})")


def main():
    """Main seeding function"""
    print("🌱 Starting appointments database seeding...")
    print("=" * 50)

    try:
        # Get experts and clients
        experts, clients = get_experts_and_clients()
        print(f"Found {len(experts)} experts and {len(clients)} clients")

        # Seed different types of appointments
        seed_pending_appointments(experts, clients, 40)
        print("-" * 30)
        seed_waiting_approval_appointments(experts, clients, 40)
        print("-" * 30)
        seed_confirmed_appointments(experts, clients, 60)
        print("-" * 30)
        seed_cancel_requested_appointments(experts, clients, 20)
        print("-" * 30)
        seed_cancelled_appointments(experts, clients, 20)
        print("-" * 30)
        seed_completed_appointments(experts, clients, 20)
        print("-" * 30)
        seed_soft_deleted_appointments(experts, clients, 10)
        print("-" * 30)

        # Count total appointments
        total_appointments = Appointment.objects.count()
        print(f"✅ Appointments database seeding completed! Total appointments: {total_appointments}")

    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()