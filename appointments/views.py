from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Appointment
from .serializers import AppointmentSerializer, CreateAppointmentWithZoomSerializer
from .permissions import IsExpertOrReadOnlyPermission, IsAppointmentParticipantPermission, IsAppointmentExpertPermission
from zoom.services import create_zoom_meeting
from datetime import datetime


class AppointmentListCreateView(generics.ListCreateAPIView):
    """
    List all appointments or create a new appointment with Zoom meeting
    """
    permission_classes = [IsExpertOrReadOnlyPermission]
    
    def get_queryset(self):
        user = self.request.user
        # Return appointments where user is either expert or client
        return Appointment.objects.filter(
            expert=user
        ) | Appointment.objects.filter(
            client=user
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AppointmentSerializer
        return CreateAppointmentWithZoomSerializer


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an appointment
    """
    permission_classes = [IsAppointmentParticipantPermission]
    serializer_class = AppointmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Appointment.objects.filter(
            expert=user
        ) | Appointment.objects.filter(
            client=user
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_appointments(request):
    """
    Get all appointments for the authenticated user
    """
    user = request.user
    appointments = Appointment.objects.filter(
        expert=user
    ) | Appointment.objects.filter(
        client=user
    ).order_by('-created_at')
    
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAppointmentExpertPermission])
def confirm_appointment(request, appointment_id):
    """
    Confirm an appointment (only expert can confirm)
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    appointment.is_confirmed = True
    appointment.status = 'confirmed'
    appointment.save()
    
    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_zoom_meeting_info(request, appointment_id):
    """
    Get Zoom meeting information for a specific appointment
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user is involved in this appointment
    if appointment.expert != request.user and appointment.client != request.user:
        return Response(
            {'error': 'Bu randevuyu görüntüleme yetkiniz yok'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    zoom_info = {
        'appointment_id': appointment.id,
        'meeting_id': appointment.zoom_meeting_id,
        'start_url': appointment.zoom_start_url,
        'join_url': appointment.zoom_join_url,
        'topic': f"Danışmanlık: {appointment.client.get_full_name()} - Uzman {appointment.expert.get_full_name()}",
        'date': appointment.date,
        'time': appointment.time,
        'duration': appointment.duration,
        'is_confirmed': appointment.is_confirmed,
        'status': appointment.status
    }
    
    return Response(zoom_info)