from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Appointment
from .serializers import (
    AppointmentSerializer,
    CreateAppointmentWithZoomSerializer,
    ClientCreateAppointmentSerializer,
    AppointmentStatusUpdateSerializer
)
from .permissions import (
    IsExpertOrClientForCreatePermission,
    IsAppointmentParticipantPermission,
    IsAppointmentExpertPermission,
    IsAppointmentClientPermission
)
from zoom.services import create_zoom_meeting
from datetime import datetime


class AppointmentListView(generics.ListAPIView):
    """
    List all appointments for authenticated user
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Return appointments where user is either expert or client
        return Appointment.objects.filter(
            expert=user
        ) | Appointment.objects.filter(
            client=user
        ).order_by('-created_at')


class ExpertAppointmentCreateView(generics.CreateAPIView):
    """
    Expert creates appointment with Zoom meeting
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateAppointmentWithZoomSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Sadece uzmanlar randevu oluşturabilir
        """
        user = request.user
        
        # Rol kontrolü
        if not hasattr(user, 'role'):
            return Response(
                {'error': 'Kullanıcı rol bilgisi bulunamadı', 'debug': f'User: {user}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user.role != 'expert':
            return Response(
                {'error': f'Sadece uzmanlar bu endpoint\'i kullanabilir. Mevcut rol: {user.role}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().create(request, *args, **kwargs)


class ClientAppointmentRequestView(generics.CreateAPIView):
    """
    Client creates appointment request
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientCreateAppointmentSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Sadece danışanlar randevu talebi oluşturabilir
        """
        user = request.user
        
        # Debug bilgileri
        print(f"User: {user}")
        print(f"User type: {type(user)}")
        print(f"Has role attr: {hasattr(user, 'role')}")
        if hasattr(user, 'role'):
            print(f"User role: {user.role}")
        
        # Rol kontrolü
        if not hasattr(user, 'role'):
            return Response(
                {'error': 'Kullanıcı rol bilgisi bulunamadı', 'debug': f'User: {user}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user.role != 'client':
            return Response(
                {'error': f'Sadece danışanlar bu endpoint\'i kullanabilir. Mevcut rol: {user.role}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().create(request, *args, **kwargs)


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
    
    def update(self, request, *args, **kwargs):
        """
        Randevu güncelleme işlemi
        """
        print(f"Update request received for user: {request.user}")
        print(f"Request data: {request.data}")
        
        instance = self.get_object()
        print(f"Found appointment: {instance.id}")
        print(f"Current status: {instance.status}")
        
        # Partial update'i destekle
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            print("Serializer is valid, saving...")
            self.perform_update(serializer)
            print(f"Updated appointment status: {serializer.instance.status}")
            return Response(serializer.data)
        else:
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Kısmi güncelleme işlemi (PATCH)
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


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
@permission_classes([permissions.IsAuthenticated])
def confirm_appointment(request, appointment_id):
    """
    Confirm an appointment (only expert can confirm)
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user is the expert of this appointment
    if appointment.expert != request.user:
        return Response(
            {'error': 'Bu randevuyu onaylama yetkiniz yok'},
            status=status.HTTP_403_FORBIDDEN
        )
    
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


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_appointment(request, appointment_id):
    """
    Danışan tarafından oluşturulan randevuyu onaylar (sadece uzman)
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user is the expert of this appointment
    if appointment.expert != request.user:
        return Response(
            {'error': 'Bu randevuyu onaylama yetkiniz yok'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Sadece waiting_approval durumundaki randevular onaylanabilir
    if appointment.status != 'waiting_approval':
        return Response(
            {'error': 'Bu randevu onay bekleyen durumda değil'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Randevuyu onayla
    appointment.status = 'confirmed'
    appointment.is_confirmed = True
    
    # Zoom meeting oluştur
    try:
        meeting_datetime = datetime.combine(appointment.date, appointment.time)
        topic = f"Danışmanlık: {appointment.client.get_full_name()} - Uzman {appointment.expert.get_full_name()}"
        
        zoom_info = create_zoom_meeting(
            topic=topic,
            start_time=meeting_datetime,
            duration=appointment.duration
        )
        
        appointment.zoom_start_url = zoom_info.get('start_url')
        appointment.zoom_join_url = zoom_info.get('join_url')
        appointment.zoom_meeting_id = str(zoom_info.get('id'))
        
    except Exception as e:
        print(f"Zoom meeting creation failed for appointment {appointment.id}: {str(e)}")
    
    appointment.save()
    
    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_request_appointment(request, appointment_id):
    """
    Danışan randevu iptal talebi gönderir
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user is the client of this appointment
    if appointment.client != request.user:
        return Response(
            {'error': 'Bu randevu için iptal talebi gönderme yetkiniz yok'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Sadece confirmed durumundaki randevular için iptal talebi gönderilebilir
    if appointment.status != 'confirmed':
        return Response(
            {'error': 'Sadece onaylanmış randevular için iptal talebi gönderilebilir'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # İptal talebi durumuna güncelle
    appointment.status = 'cancel_requested'
    appointment.save()
    
    return Response({
        'id': appointment.id,
        'status': appointment.status,
        'message': 'İptal talebi gönderildi, uzman onayı bekleniyor.'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_confirm_appointment(request, appointment_id):
    """
    Uzman iptal talebini onaylar veya reddeder
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user is the expert of this appointment
    if appointment.expert != request.user:
        return Response(
            {'error': 'Bu randevunun iptal talebini değerlendirme yetkiniz yok'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Sadece cancel_requested durumundaki randevular işlenebilir
    if appointment.status != 'cancel_requested':
        return Response(
            {'error': 'Bu randevu iptal talebi bekleyen durumda değil'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = AppointmentStatusUpdateSerializer(data=request.data)
    if serializer.is_valid():
        confirm = serializer.validated_data['confirm']
        
        if confirm:
            # İptal talebi onaylandı
            appointment.status = 'cancelled'
            appointment.is_confirmed = False
        else:
            # İptal talebi reddedildi, confirmed durumuna geri dön
            appointment.status = 'confirmed'
        
        appointment.save()
        
        response_data = {
            'id': appointment.id,
            'status': appointment.status
        }
        
        if confirm:
            response_data['message'] = 'Randevu iptal edildi'
        else:
            response_data['message'] = 'İptal talebi reddedildi'
        
        return Response(response_data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)