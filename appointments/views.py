from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Appointment
from .serializers import (
    AppointmentSerializer,
    CreateAppointmentWithZoomSerializer,
    ClientCreateAppointmentSerializer,
    AppointmentStatusSerializer
)
from .permissions import (
    IsExpertOrClientForCreatePermission,
    IsAppointmentParticipantPermission,
    IsAppointmentExpertPermission,
    IsAppointmentClientPermission
)
from accounts.models import UserRole
from zoom.services import create_zoom_meeting
from datetime import datetime


class AppointmentListView(generics.ListAPIView):
    """
    Kullanıcı rolüne ve mine parametresine göre randevuları listele
    Sorgu parametreleri:
    - mine: boolean - true ise kullanıcının kendi randevularını döndürür; false veya verilmediği durumda adminler tüm randevuları, diğerleri kendi randevularını görür
    - status: randevu durumuna göre filtrele
    Geçerli durum değerleri: pending, waiting_approval, confirmed, cancel_requested, cancelled, completed
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        user = self.request.user

        # Check mine parameter
        mine_param = self.request.query_params.get('mine', '').lower()
        mine = mine_param in ['true', '1', 'yes']

        if mine:
            # Return user's own appointments
            queryset = Appointment.objects.filter(
                expert=user
            ) | Appointment.objects.filter(
                client=user
            )
        else:
            # If mine is false or not provided
            if hasattr(user, 'role') and user.role == UserRole.ADMIN:
                # Admins get all appointments
                queryset = Appointment.objects.all()
            else:
                # Non-admins get their own appointments
                queryset = Appointment.objects.filter(
                    expert=user
                ) | Appointment.objects.filter(
                    client=user
                )

        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            # Validate status parameter
            valid_statuses = ['pending', 'waiting_approval', 'confirmed', 'cancel_requested', 'cancelled', 'completed']
            if status_filter not in valid_statuses:
                # Return empty queryset for invalid status
                return Appointment.objects.none()
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')


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

    def status_update(self, request, *args, **kwargs):
        """
        Randevu durumu güncelleme endpoint'i
        PATCH /appointments/{id}/status
        """
        if request.method != 'PATCH':
            return Response(
                {'error': 'Bu endpoint sadece PATCH isteklerini kabul eder'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        instance = self.get_object()
        user = request.user

        # Serializer ile gelen veriyi doğrula
        serializer = AppointmentStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status = serializer.validated_data['status']
        current_status = instance.status

        # Durum geçişi validasyonları
        if new_status == current_status:
            return Response(
                {'error': f'Randevu zaten "{current_status}" durumunda'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Geçiş kuralları
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],  # uzman pending'den confirmed veya cancelled yapabilir
            'waiting_approval': ['confirmed', 'cancelled'],  # uzman waiting_approval'dan confirmed veya cancelled yapabilir
            'confirmed': ['cancel_requested', 'completed'],  # danışan confirmed'dan cancel_requested, uzman completed yapabilir
            'cancel_requested': ['cancelled', 'confirmed'],  # uzman cancel_requested'den cancelled veya confirmed yapabilir
            'cancelled': [],  # cancelled durumundan çıkış yok
            'completed': []  # completed durumundan çıkış yok
        }

        if new_status not in valid_transitions.get(current_status, []):
            return Response(
                {'error': f'"{current_status}" durumundan "{new_status}" durumuna geçiş yapılamaz'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Kullanıcı yetki kontrolü
        if new_status in ['confirmed', 'cancelled', 'completed']:
            # Sadece uzman bu durumları değiştirebilir
            if instance.expert != user:
                return Response(
                    {'error': 'Bu durumu değiştirmek için uzman olmanız gerekir'},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif new_status == 'cancel_requested':
            # Sadece danışan cancel_requested yapabilir
            if instance.client != user:
                return Response(
                    {'error': 'İptal talebi sadece danışan tarafından yapılabilir'},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Durumu güncelle
        instance.status = new_status

        # Özel durum işlemleri
        if new_status == 'confirmed':
            instance.is_confirmed = True
            # Zoom meeting oluştur (eğer yoksa)
            if not instance.zoom_meeting_id:
                try:
                    meeting_datetime = datetime.combine(instance.date, instance.time)
                    topic = f"Danışmanlık: {instance.client.get_full_name()} - Uzman {instance.expert.get_full_name()}"

                    # zoom_info = create_zoom_meeting(
                    #     topic=topic,
                    #     start_time=meeting_datetime,
                    #     duration=instance.duration
                    # )
                    # Mocked for example purposes
                    zoom_info = {"start_url":"status update mock url",
                                "join_url":"status update mock url",
                                "id":"status update mock url"}

                    instance.zoom_start_url = zoom_info.get('start_url')
                    instance.zoom_join_url = zoom_info.get('join_url')
                    instance.zoom_meeting_id = str(zoom_info.get('id'))

                except Exception as e:
                    print(f"Zoom meeting creation failed for appointment {instance.id}: {str(e)}")

        elif new_status == 'cancelled':
            instance.is_confirmed = False

        instance.save()

        # Response serializer ile döndür
        response_serializer = AppointmentSerializer(instance)
        return Response(response_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: kaydı silmek yerine is_deleted=True yapar
        """
        instance = self.get_object()
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted", "updated_at"])
        return Response({"detail": "Appointment marked as deleted."}, status=status.HTTP_204_NO_CONTENT)


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
