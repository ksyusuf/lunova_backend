from rest_framework import serializers
from .models import WeeklyAvailability, AvailabilityException


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
        user = self.context['request'].user
        if not hasattr(user, 'role') or user.role != 'expert':
            raise serializers.ValidationError("Sadece uzmanlar müsaitlik istisnası tanımlayabilir.")
        
        # Add tipinde start_time ve end_time zorunlu
        if data.get('exception_type') == 'add':
            if not data.get('start_time') or not data.get('end_time'):
                raise serializers.ValidationError("Ekstra müsaitlik için başlangıç ve bitiş saati zorunludur.")
            
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("Başlangıç saati bitiş saatinden önce olmalıdır.")
        
        return data


class BulkWeeklyAvailabilitySerializer(serializers.Serializer):
    availabilities = WeeklyAvailabilitySerializer(many=True)
    
    def create(self, validated_data):
        availabilities_data = validated_data['availabilities']
        created_availabilities = []
        
        for availability_data in availabilities_data:
            availability_data['expert'] = self.context['request'].user.expertprofile
            availability = WeeklyAvailability.objects.create(**availability_data)
            created_availabilities.append(availability)
        
        return {'availabilities': created_availabilities}


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
