from rest_framework import serializers
from .models import Appointment
from zoom.services import create_zoom_meeting
from datetime import datetime
from django.conf import settings
from availability.models import WeeklyAvailability, AvailabilityException


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
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'expert', 'client', 'expert_name', 'client_name',
            'date', 'time', 'duration', 'notes', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Danışan randevu oluştururken gerekli validasyonlar
        """
        # Ek güvenlik kontrolü: Sadece danışanlar randevu talebi oluşturabilir
        user = self.context['request'].user
        if not hasattr(user, 'role') or user.role != 'client':
            raise serializers.ValidationError("Sadece danışanlar bu şekilde randevu talebi oluşturabilir.")

        # Expert zorunlu
        if 'expert' not in data:
            raise serializers.ValidationError("Uzman seçimi zorunludur.")

        # Tarih ve saat zorunlu
        if 'date' not in data or 'time' not in data:
            raise serializers.ValidationError("Tarih ve saat bilgisi zorunludur.")

        expert = data['expert']
        appointment_date = data['date']
        appointment_time = data['time']

        # 1. Uzmanın başka randevusu var mı kontrol et (expert ve client bağımsız)
        existing_appointment = Appointment.objects.filter(
            expert=expert,
            date=appointment_date,
            time=appointment_time,
            status__in=['pending', 'waiting_approval', 'confirmed'],
            is_deleted=False
        ).exists()

        if existing_appointment:
            raise serializers.ValidationError(
                "Bu tarih ve saatte uzmanın başka bir randevusu bulunmaktadır."
            )

        # 2. Client'ın aynı saatte başka randevusu var mı kontrol et
        client_existing_appointment = Appointment.objects.filter(
            client=user,
            date=appointment_date,
            time=appointment_time,
            status__in=['pending', 'waiting_approval', 'confirmed'],
            is_deleted=False
        ).exists()

        if client_existing_appointment:
            raise serializers.ValidationError(
                "Bu tarih ve saatte sizin başka bir randevunuz bulunmaktadır."
            )

        # 3. Uzmanın weekly availability kontrolü
        day_of_week = appointment_date.weekday()  # 0=Monday, 6=Sunday

        weekly_available = WeeklyAvailability.objects.filter(
            expert__user=expert,
            day_of_week=day_of_week,
            start_time__lte=appointment_time,
            end_time__gt=appointment_time,  # end_time > appointment_time (çakışmayı önlemek için)
            is_active=True
        ).exists()

        if not weekly_available:
            raise serializers.ValidationError(
                "Uzman bu tarih ve saatte müsait değildir (haftalık program)."
            )

        # 4. Availability exceptions kontrolü
        # Önce normal tarih için kontrol et
        exception = AvailabilityException.objects.filter(
            expert__user=expert,
            date=appointment_date,
            exception_type='cancel'
        ).first()

        if exception:
            # İptal exception'ı varsa, saat kontrolü yap
            if (exception.start_time and exception.end_time and
                exception.start_time <= appointment_time < exception.end_time):
                raise serializers.ValidationError(
                    "Uzman bu tarih ve saatte müsait değildir (özel istisna)."
                )
            elif not exception.start_time and not exception.end_time:
                # Tüm gün iptal
                raise serializers.ValidationError(
                    "Uzman bu tarihte müsait değildir (özel istisna)."
                )

        # Tekrarlayan istisnalar için kontrol (her yıl aynı tarih)
        recurring_exceptions = AvailabilityException.objects.filter(
            expert__user=expert,
            date__month=appointment_date.month,
            date__day=appointment_date.day,
            is_recurring=True,
            exception_type='cancel'
        )

        for rec_exception in recurring_exceptions:
            if (rec_exception.start_time and rec_exception.end_time and
                rec_exception.start_time <= appointment_time < rec_exception.end_time):
                raise serializers.ValidationError(
                    "Uzman bu tarih ve saatte müsait değildir (tekrarlayan istisna)."
                )
            elif not rec_exception.start_time and not rec_exception.end_time:
                raise serializers.ValidationError(
                    "Uzman bu tarihte müsait değildir (tekrarlayan istisna)."
                )

        return data
    
    def create(self, validated_data):
        """
        Danışan randevusu oluştur - waiting_approval durumunda
        """
        # Danışan randevusu waiting_approval durumunda oluşturulur
        validated_data['status'] = 'waiting_approval'
        
        appointment = Appointment.objects.create(**validated_data)
        
        # Zoom meeting oluşturulmaz, sadece onaylandığında oluşturulur
        
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