from rest_framework import serializers
from .models import WeeklyAvailability, AvailabilityException, Service


class WeeklyAvailabilitySerializer(serializers.ModelSerializer):
    expert_name = serializers.CharField(source='expert.user.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    timezone = serializers.CharField(source='expert.timezone', read_only=True)
    
    class Meta:
        model = WeeklyAvailability
        fields = [
            'id', 'expert', 'expert_name', 'day_of_week', 'day_display',
            'start_time', 'end_time', 'timezone', 'service', 'service_name',
            'is_active', 'slot_minutes', 'capacity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['expert', 'created_at', 'updated_at']
    
    def validate(self, data):
        # Expert rolü kontrolü
        user = self.context['request'].user
        if not hasattr(user, 'role') or user.role != 'expert':
            raise serializers.ValidationError("Sadece uzmanlar müsaitlik tanımlayabilir.")
        
        # Start time < end time kontrolü
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("Başlangıç saati bitiş saatinden önce olmalıdır.")
        
        return data
   
    
class WeeklyAvailabilityDeleteSerializer(serializers.Serializer):
    day_of_week = serializers.IntegerField(
        min_value=0, 
        max_value=6, 
        help_text="0=Pazartesi, 6=Pazar"
    )
    start_time = serializers.TimeField(help_text="Başlangıç saati (HH:MM:SS)")
    end_time = serializers.TimeField(help_text="Bitiş saati (HH:MM:SS)")
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), 
        required=False,
        help_text="Opsiyonel: sadece bu servis için sil"
    )

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Başlangıç saati bitiş saatinden önce olmalıdır.")
        return data


class AvailabilityExceptionSerializer(serializers.ModelSerializer):
    expert_name = serializers.CharField(source='expert.user.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = AvailabilityException
        fields = [
            'id', 'expert', 'expert_name', 'date', 'exception_type',
            'start_time', 'end_time', 'service', 'service_name',
            'note', 'created_at'
        ]
        read_only_fields = ['expert', 'created_at']
    
    def validate(self, data):
        # Add tipinde start_time ve end_time zorunlu
        if data.get('exception_type') == 'add':
            if not data.get('start_time') or not data.get('end_time'):
                raise serializers.ValidationError("Ekstra müsaitlik için başlangıç ve bitiş saati zorunludur.")
            
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("Başlangıç saati bitiş saatinden önce olmalıdır.")
        
        return data


class AvailabilityExceptionDeleteSerializer(serializers.Serializer):
    """
    AvailabilityException kaydını silmek için gereken doğrulama:
    id + date + start_time + end_time zorunludur.
    """
    id = serializers.IntegerField(
        required=True,
        help_text="Silinecek istisnanın ID değeri (zorunlu)."
    )
    date = serializers.DateField(
        required=True,
        help_text="Silinecek istisnanın tarihi (YYYY-MM-DD, zorunlu)."
    )
    start_time = serializers.TimeField(
        required=True,
        help_text="Başlangıç saati (HH:MM:SS, zorunlu)."
    )
    end_time = serializers.TimeField(
        required=True,
        help_text="Bitiş saati (HH:MM:SS, zorunlu)."
    )

    def validate(self, data):
        """
        Tüm alanlar zorunlu.
        Başlangıç saati bitiş saatinden önce olmalı.
        """
        if not all(field in data for field in ['id', 'date', 'start_time', 'end_time']):
            raise serializers.ValidationError(
                "Silme işlemi için id, date, start_time ve end_time alanlarının tümü zorunludur."
            )

        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Başlangıç saati bitiş saatinden önce olmalıdır.")

        return data


    

class BulkWeeklyAvailabilitySerializer(serializers.Serializer):
    availabilities = WeeklyAvailabilitySerializer(many=True)
    
    def create(self, validated_data):
        availabilities_data = validated_data['availabilities']
        added = []
        skipped = []

        expert = self.context['request'].user.expertprofile

        for availability_data in availabilities_data:
            availability_data['expert'] = expert
            
            # Tekil kısıt kontrolü
            exists = WeeklyAvailability.objects.filter(
                expert=expert,
                service=availability_data['service'],
                day_of_week=availability_data['day_of_week'],
                start_time=availability_data['start_time'],
                end_time=availability_data['end_time']
            ).exists()

            if exists:
                skipped.append(availability_data)
                continue

            # Kayıt oluştur
            wa = WeeklyAvailability.objects.create(**availability_data)
            added.append(wa)

        return {'added': added, 'skipped': skipped}


class BulkAvailabilityExceptionSerializer(serializers.Serializer):
    exceptions = AvailabilityExceptionSerializer(many=True)
    
    def create(self, validated_data):
        exceptions_data = validated_data['exceptions']
        created_exceptions = []
        
        for exception_data in exceptions_data:
            exception_data['expert'] = self.context['request'].user.expertprofile
            exception = AvailabilityException.objects.create(**exception_data)
            created_exceptions.append(exception)
        
        return {'exceptions': created_exceptions}
