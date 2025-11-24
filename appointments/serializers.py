from rest_framework import serializers
from .models import Appointment
from zoom.services import create_zoom_meeting
from datetime import datetime
from django.conf import settings
from availability.models import WeeklyAvailability, AvailabilityException
from accounts.models import ExpertProfile, User


class AppointmentSerializer(serializers.ModelSerializer):
    expert_name = serializers.CharField(source='expert.get_full_name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'expert', 'client', 'expert_name', 'client_name',
            'date', 'time', 'duration', 'is_confirmed', 'notes', 'status',
            'zoom_start_url', 'zoom_join_url', 'zoom_meeting_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['zoom_start_url', 'zoom_join_url', 'zoom_meeting_id', 'created_at', 'updated_at']


class CreateAppointmentWithZoomSerializer(serializers.ModelSerializer):
    expert_name = serializers.CharField(source='expert.get_full_name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'expert', 'client', 'expert_name', 'client_name',
            'date', 'time', 'duration', 'is_confirmed', 'notes', 'status',
            'zoom_start_url', 'zoom_join_url', 'zoom_meeting_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['zoom_start_url', 'zoom_join_url', 'zoom_meeting_id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Uzman randevu oluştururken gerekli validasyonlar
        """
        # Ek güvenlik kontrolü: Sadece uzmanlar randevu oluşturabilir
        user = self.context['request'].user
        if not hasattr(user, 'role') or user.role != 'expert':
            raise serializers.ValidationError("Sadece uzmanlar bu şekilde randevu oluşturabilir.")
        
        # Expert zorunlu
        if 'expert' not in data:
            raise serializers.ValidationError("Uzman seçimi zorunludur.")
        
        # Tarih ve saat zorunlu
        if 'date' not in data or 'time' not in data:
            raise serializers.ValidationError("Tarih ve saat bilgisi zorunludur.")
        
        # Aynı tarih+saat için uzmanın başka randevusu var mı kontrol et
        existing_appointment = Appointment.objects.filter(
            expert=data['expert'],
            date=data['date'],
            time=data['time'],
            status__in=['pending', 'waiting_approval', 'confirmed']
        ).exists()
        
        if existing_appointment:
            raise serializers.ValidationError(
                "Bu tarih ve saatte uzmanın başka bir randevusu bulunmaktadır."
            )
        
        return data
    
    def create(self, validated_data):
        """Create appointment and automatically create Zoom meeting"""
        appointment = Appointment.objects.create(**validated_data)
        
        # Create Zoom meeting for this appointment
        try:
            # Combine date and time for Zoom meeting
            meeting_datetime = datetime.combine(
                validated_data['date'], 
                validated_data['time']
            )
            
            # Create topic with expert and client names
            topic = f"Danışmanlık: {validated_data['client'].get_full_name()} - Uzman {validated_data['expert'].get_full_name()}"
            
            # Environment kontrolü
            if settings.ENVIRONMENT == 'Production':
                # Production'da gerçek Zoom meeting oluştur
                zoom_info = create_zoom_meeting(
                    topic=topic,
                    start_time=meeting_datetime,
                    duration=validated_data.get('duration', 45)
                )
            else:
                # Development'ta mock veri kullan
                zoom_info = {
                    "start_url": "mock url",
                    "join_url": "mock url",
                    "id": f"mock_meeting_{appointment.id}"
                }
            
            # Update appointment with Zoom details
            appointment.zoom_start_url = zoom_info.get('start_url')
            appointment.zoom_join_url = zoom_info.get('join_url')
            appointment.zoom_meeting_id = str(zoom_info.get('id'))
            appointment.save()
            
        except Exception as e:
            # Log error but don't fail the appointment creation
            print(f"Zoom meeting creation failed for appointment {appointment.id}: {str(e)}")
        
        return appointment


class ClientCreateAppointmentSerializer(serializers.ModelSerializer):
    """
    Danışanların randevu oluşturması için serializer
    """
    expert_name = serializers.CharField(source='expert.get_full_name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    client = serializers.HiddenField(default=serializers.CurrentUserDefault())
    expert_user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'expert', 'expert_user_id', 'client', 'expert_name', 'client_name',
            'date', 'time', 'duration', 'notes', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['expert', 'status', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Danışan randevu oluştururken gerekli validasyonlar ve ID/Nesne dönüşümü
        """
        user = self.context['request'].user
        
        # Güvenlik ve Zorunluluk Kontrolleri
        if not hasattr(user, 'role') or user.role != 'client':
            raise serializers.ValidationError("Sadece danışanlar bu şekilde randevu talebi oluşturabilir.")

        expert_uid = data.get('expert_user_id')
        if not expert_uid:
            raise serializers.ValidationError("Uzman seçimi zorunludur.")
            
        if 'date' not in data or 'time' not in data:
            raise serializers.ValidationError("Tarih ve saat bilgisi zorunludur.")

        appointment_date = data['date']
        appointment_time = data['time']

        try:
            # ExpertProfile, User ID ile ilişkili olduğu için çekilir.
            expert_profile = ExpertProfile.objects.get(user_id=expert_uid)
        except ExpertProfile.DoesNotExist:
            raise serializers.ValidationError({"expert_user_id": "Seçilen ID ile eşleşen bir uzman profili bulunamadı."})
            
        # --- ADIM 2: User Nesnesini Çekme (Appointment kaydı için zorunlu) ---
        # Appointment.expert = User nesnesi beklediği için çekilir.
        try:
             expert_user_obj = User.objects.get(id=expert_uid)
        except User.DoesNotExist:
             raise serializers.ValidationError({"expert_user_id": "Kullanıcı bulunamadı."})

        # --- ADIM 3: Appointment Modeli için User Nesnesini Atama ---
        data['expert'] = expert_user_obj 

        # 1. Uzmanın başka randevusu var mı kontrol et (Appointment.expert -> User)
        existing_appointment = Appointment.objects.filter(
            expert_id=expert_uid,
            date=appointment_date,
            time=appointment_time,
            status='confirmed',
            is_deleted=False
        ).exists()

        if existing_appointment:
            raise serializers.ValidationError("Bu tarih ve saatte uzmanın başka bir randevusu bulunmaktadır.")

        # 2. Client'ın aynı saatte başka randevusu var mı kontrol et (Appointment.client -> User)
        existing_appointment = Appointment.objects.filter(
            client_id=user.id, # En güvenli ve direkt sorgulama yöntemi.
            date=appointment_date,
            time=appointment_time,
            is_deleted=False
        ).first()

        if existing_appointment:
            if existing_appointment.status == 'waiting_approval':
                raise serializers.ValidationError("Bu saat için onay bekleyen bir randevunuz var.")
            elif existing_appointment.status == 'pending':
                raise serializers.ValidationError("Bu saat için uzman onayı bekleyen başka bir randevunuz bulunuyor.")
            elif existing_appointment.status == 'confirmed':
                raise serializers.ValidationError("Bu saat için onaylanmış başka bir randevunuz var.")

        # 3. Uzmanın weekly availability kontrolü (WeeklyAvailability.expert -> ExpertProfile)
        day_of_week = appointment_date.weekday()

        # ExpertProfile nesnesini (expert_profile) kullanarak sorgu yapıyoruz.
        weekly_available = WeeklyAvailability.objects.filter(
            expert=expert_profile,
            day_of_week=day_of_week,
            start_time__lte=appointment_time,
            end_time__gt=appointment_time,
            is_active=True
        ).exists()

        if not weekly_available:
            raise serializers.ValidationError("Uzman bu tarih ve saatte müsait değildir (haftalık program).")

        # 4. Availability exceptions kontrolü (AvailabilityException.expert -> ExpertProfile)
        # Önce normal tarih için kontrol et
        exception = AvailabilityException.objects.filter(
            expert=expert_profile,
            date=appointment_date,
            exception_type='cancel'
        ).first()

        if exception:
            if (exception.start_time and exception.end_time and
                exception.start_time <= appointment_time < exception.end_time):
                raise serializers.ValidationError("Uzman bu tarih ve saatte müsait değildir (özel istisna).")
            elif not exception.start_time and not exception.end_time:
                raise serializers.ValidationError("Uzman bu tarihte müsait değildir (özel istisna).")

        # Tekrarlayan istisnalar için kontrol
        recurring_exceptions = AvailabilityException.objects.filter(
            expert=expert_profile,
            date__month=appointment_date.month,
            date__day=appointment_date.day,
            is_recurring=True,
            exception_type='cancel'
        )

        for rec_exception in recurring_exceptions:
            if (rec_exception.start_time and rec_exception.end_time and
                rec_exception.start_time <= appointment_time < rec_exception.end_time):
                raise serializers.ValidationError("Uzman bu tarih ve saatte müsait değildir (tekrarlayan istisna).")
            elif not rec_exception.start_time and not rec_exception.end_time:
                raise serializers.ValidationError("Uzman bu tarihte müsait değildir (tekrarlayan istisna).")

        return data
    
    def create(self, validated_data):
        """
        Danışan randevusu oluştur - waiting_approval durumunda
        """
        # Giriş amaçlı kullanılan expert_user_id tamsayısını kaldırıyoruz.
        validated_data.pop('expert_user_id')
        
        # 'expert' anahtarında User nesnesi mevcut.
        validated_data['status'] = 'waiting_approval'
        
        appointment = Appointment.objects.create(**validated_data)
        
        return appointment


class AppointmentStatusSerializer(serializers.Serializer):
    """
    Randevu durumu güncelleme için yeni serializer
    """
    status = serializers.ChoiceField(
        choices=[
            ('pending', 'Beklemede'),
            ('waiting_approval', 'Onay Bekliyor'),
            ('confirmed', 'Onaylandı'),
            ('cancel_requested', 'İptal Talep Edildi'),
            ('cancelled', 'İptal Edildi'),
            ('completed', 'Tamamlandı'),
        ],
        required=True
    )


class ExpertAppointmentSummarySerializer(serializers.ModelSerializer):
    """
    Expert appointments summary for clients - shows only essential info
    danışan, randevu oluştururken bu uzmanın o tarih saatte müsaitliğini
    görüp ona göre randevu isteği göndermesi için tasarlandı.
    """
    start_time = serializers.TimeField(source='time', read_only=True)
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id', 'date', 'start_time', 'end_time', 'status']

    def get_end_time(self, obj):
        from datetime import datetime, timedelta
        # Buffer süreleri: 30->15, 45->20, 60->30 dakika
        """
            30 -> 20
            50 -> 30
            randevu süresi ve mola süresi önerilen olarakk böyle.
            iki tip seansımızın olması uygun gözüküyor. daha sonra rezervasyon oluşturma
            ksımında bir kısıt oluştururuz.
        """
        buffer_minutes = {30:20, 45: 20, 60: 30}.get(obj.duration, 0)
        total_minutes = obj.duration + buffer_minutes

        # Randevu başlangıç datetime
        start_datetime = datetime.combine(obj.date, obj.time)
        # Bitiş datetime
        end_datetime = start_datetime + timedelta(minutes=total_minutes)

        return end_datetime.time()