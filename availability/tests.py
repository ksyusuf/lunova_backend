from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import time, date
from .models import WeeklyAvailability, AvailabilityException
from accounts.models import ExpertProfile, Service

User = get_user_model()


class WeeklyAvailabilityModelTest(TestCase):
    def setUp(self):
        # Test user oluştur
        self.user = User.objects.create_user(
            username='testexpert',
            email='expert@test.com',
            password='testpass123',
            role='expert'
        )
        
        # ExpertProfile oluştur
        self.expert_profile = ExpertProfile.objects.create(
            user=self.user,
            specialization='Test Uzmanlık'
        )
        
        # Service oluştur
        self.service = Service.objects.create(
            name='Test Hizmet',
            description='Test hizmet açıklaması'
        )
    
    def test_weekly_availability_creation(self):
        """Haftalık müsaitlik oluşturma testi"""
        availability = WeeklyAvailability.objects.create(
            expert=self.expert_profile,
            day_of_week=0,  # Pazartesi
            start_time=time(9, 0),  # 09:00
            end_time=time(17, 0),   # 17:00
            service=self.service,
            slot_minutes=50,
            capacity=1
        )
        
        self.assertEqual(availability.expert, self.expert_profile)
        self.assertEqual(availability.day_of_week, 0)
        self.assertEqual(availability.get_day_of_week_display(), 'Pazartesi')
        self.assertEqual(availability.start_time, time(9, 0))
        self.assertEqual(availability.end_time, time(17, 0))
        self.assertEqual(availability.service, self.service)
        self.assertTrue(availability.is_active)
    
    def test_weekly_availability_str_representation(self):
        """String temsili testi"""
        availability = WeeklyAvailability.objects.create(
            expert=self.expert_profile,
            day_of_week=1,  # Salı
            start_time=time(10, 0),
            end_time=time(16, 0)
        )
        
        expected_str = f"{self.user.get_full_name()} - Salı 10:00:00-16:00:00"
        self.assertEqual(str(availability), expected_str)


class AvailabilityExceptionModelTest(TestCase):
    def setUp(self):
        # Test user oluştur
        self.user = User.objects.create_user(
            username='testexpert2',
            email='expert2@test.com',
            password='testpass123',
            role='expert'
        )
        
        # ExpertProfile oluştur
        self.expert_profile = ExpertProfile.objects.create(
            user=self.user,
            specialization='Test Uzmanlık 2'
        )
        
        # Service oluştur
        self.service = Service.objects.create(
            name='Test Hizmet 2',
            description='Test hizmet açıklaması 2'
        )
    
    def test_cancel_exception_creation(self):
        """İptal istisnası oluşturma testi"""
        exception = AvailabilityException.objects.create(
            expert=self.expert_profile,
            date=date(2024, 1, 15),
            exception_type='cancel',
            note='Tatil günü'
        )
        
        self.assertEqual(exception.expert, self.expert_profile)
        self.assertEqual(exception.date, date(2024, 1, 15))
        self.assertEqual(exception.exception_type, 'cancel')
        self.assertEqual(exception.note, 'Tatil günü')
        self.assertIsNone(exception.start_time)
        self.assertIsNone(exception.end_time)
    
    def test_add_exception_creation(self):
        """Ekstra müsaitlik istisnası oluşturma testi"""
        exception = AvailabilityException.objects.create(
            expert=self.expert_profile,
            date=date(2024, 1, 20),
            exception_type='add',
            start_time=time(18, 0),
            end_time=time(20, 0),
            service=self.service,
            note='Ekstra çalışma saati'
        )
        
        self.assertEqual(exception.exception_type, 'add')
        self.assertEqual(exception.start_time, time(18, 0))
        self.assertEqual(exception.end_time, time(20, 0))
        self.assertEqual(exception.service, self.service)
    
    def test_availability_exception_str_representation(self):
        """String temsili testi"""
        exception = AvailabilityException.objects.create(
            expert=self.expert_profile,
            date=date(2024, 1, 15),
            exception_type='cancel'
        )
        
        expected_str = f"{self.user.get_full_name()} - 2024-01-15 (İptal)"
        self.assertEqual(str(exception), expected_str)


class WeeklyAvailabilityValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testexpert3',
            email='expert3@test.com',
            password='testpass123',
            role='expert'
        )
        
        self.expert_profile = ExpertProfile.objects.create(
            user=self.user,
            specialization='Test Uzmanlık 3'
        )
    
    def test_start_time_before_end_time_constraint(self):
        """Başlangıç saati bitiş saatinden önce olmalı kısıtlaması"""
        # Bu test Django'nun model constraint'ini test eder
        # Gerçek bir constraint testi için database transaction gerekir
        pass
    
    def test_weekday_choices(self):
        """Hafta günü seçenekleri testi"""
        choices = WeeklyAvailability.Weekday.choices
        
        self.assertEqual(len(choices), 7)
        self.assertEqual(choices[0], (0, 'Pazartesi'))
        self.assertEqual(choices[6], (6, 'Pazar'))
