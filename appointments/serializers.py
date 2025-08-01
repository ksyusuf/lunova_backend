from rest_framework import serializers
from .models import Appointment
from zoom.services import create_zoom_meeting
from datetime import datetime


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
    
    def create(self, validated_data):
        """Create appointment and automatically create Zoom meeting"""
        # Ek güvenlik kontrolü: Sadece uzmanlar randevu oluşturabilir
        user = self.context['request'].user
        if not hasattr(user, 'role') or user.role != 'expert':
            raise serializers.ValidationError("Sadece uzmanlar randevu oluşturabilir.")
        
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
            
            zoom_info = create_zoom_meeting(
                topic=topic,
                start_time=meeting_datetime,
                duration=validated_data.get('duration', 45)
            )
            
            # Update appointment with Zoom details
            appointment.zoom_start_url = zoom_info.get('start_url')
            appointment.zoom_join_url = zoom_info.get('join_url')
            appointment.zoom_meeting_id = str(zoom_info.get('id'))
            appointment.save()
            
        except Exception as e:
            # Log error but don't fail the appointment creation
            print(f"Zoom meeting creation failed for appointment {appointment.id}: {str(e)}")
        
        return appointment