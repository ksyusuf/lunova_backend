from rest_framework import serializers
from zoom.services import create_zoom_meeting


class CreateMeetingSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=200, help_text="Meeting topic/title")
    start_time = serializers.DateTimeField(required=False, help_text="Meeting start time (ISO format)")
    duration = serializers.IntegerField(default=45, min_value=15, max_value=480, help_text="Meeting duration in minutes")
    
    def create(self, validated_data):
        """Create a Zoom meeting and return meeting details"""
        try:
            zoom_info = create_zoom_meeting(
                topic=validated_data['topic'],
                start_time=validated_data.get('start_time'),
                duration=validated_data.get('duration', 45)
            )
            
            return {
                'success': True,
                'meeting_id': zoom_info.get('id'),
                'start_url': zoom_info.get('start_url'),
                'join_url': zoom_info.get('join_url'),
                'topic': zoom_info.get('topic'),
                'start_time': zoom_info.get('start_time'),
                'duration': zoom_info.get('duration'),
                'password': zoom_info.get('password'),
                'host_email': zoom_info.get('host_email')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 