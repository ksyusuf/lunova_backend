from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Appointment
from .serializers import (
    AppointmentSerializer,
    CreateAppointmentWithZoomSerializer,
    ClientCreateAppointmentSerializer,
    AppointmentStatusSerializer,
    ExpertAppointmentSummarySerializer
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
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class AppointmentListView(generics.ListAPIView):
    """
    Kullanıcı rolüne göre randevuları listele
    Sorgu parametreleri:
    - start_date: YYYY-MM-DD formatında başlangıç tarihi (zorunlu)
    - end_date: YYYY-MM-DD formatında bitiş tarihi (zorunlu)
    - status: randevu durumuna göre filtrele
    Geçerli durum değerleri: pending, waiting_approval, confirmed, cancel_requested, cancelled, completed
    Tarih aralığı: Adminler için maksimum 6 ay, diğerleri için maksimum 4 ay
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer

    def list(self, request, *args, **kwargs):
        user = self.request.user

        # Get date parameters
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')

        # Validate required parameters
        if not start_date_str:
            return Response(
                {'error': 'start_date parametresi zorunludur'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not end_date_str:
            return Response(
                {'error': 'end_date parametresi zorunludur'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Tarih formatı YYYY-MM-DD olmalıdır'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate date range
        if start_date > end_date:
            return Response(
                {'error': 'start_date, end_date\'den büyük olamaz'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check maximum allowed range
        max_months = 6 if hasattr(user, 'role') and user.role == UserRole.ADMIN else 4
        max_end_date = start_date + relativedelta(months=max_months)

        if end_date > max_end_date:
            return Response(
                {'error': f'Tarih aralığı maksimum {max_months} ay olabilir'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate status parameter if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            valid_statuses = ['pending', 'waiting_approval', 'confirmed', 'cancel_requested', 'cancelled', 'completed']
            if status_filter not in valid_statuses:
                return Response(
                    {'error': f'Geçersiz status değeri. Geçerli değerler: {", ".join(valid_statuses)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Get queryset
        queryset = self.get_queryset()

        # Apply filters
        queryset = queryset.filter(
            date__range=[start_date, end_date],
            is_deleted=False
        )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Serialize and return
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user

        # Base queryset for user's appointments
        return Appointment.objects.filter(
            expert=user
        ) | Appointment.objects.filter(
            client=user
        )


class ExpertAppointmentCreateView(generics.CreateAPIView):
    """
    Expert creates appointment with Zoom meeting
    """
    permission_classes = [IsAppointmentExpertPermission]
    serializer_class = CreateAppointmentWithZoomSerializer


class ClientAppointmentRequestView(generics.CreateAPIView):
    """
    Client creates appointment request
    """
    permission_classes = [IsAppointmentClientPermission]
    serializer_class = ClientCreateAppointmentSerializer


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

    def partial_update(self, request, *args, **kwargs):
        """
        Kısmi güncelleme işlemi (PATCH)
        Sadece kendi randevularını güncelleyebilir
        """
        print(f"PATCH request received for user: {request.user}")
        print(f"Request data: {request.data}")

        instance = self.get_object()
        print(f"Found appointment: {instance.id}")
        print(f"Current status: {instance.status}")

        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            print("Serializer is valid, saving...")
            self.perform_update(serializer)
            print(f"Updated appointment: {serializer.instance.id}")
            return Response(serializer.data)
        else:
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def status_update(self, request, *args, **kwargs):
        """
        Randevu durumu güncelleme endpoint'i
        PATCH /appointments/{id}/status
        Sadece kendi randevularını güncelleyebilir
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

                    # Environment kontrolü
                    if settings.ENVIRONMENT == 'Production':
                        # Production'da gerçek Zoom meeting oluştur
                        zoom_info = create_zoom_meeting(
                            topic=topic,
                            start_time=meeting_datetime,
                            duration=instance.duration
                        )
                    else:
                        # Development'ta mock veri kullan
                        zoom_info = {
                            "start_url": "mock url",
                            "join_url": "mock url",
                            "id": f"mock_meeting_{instance.id}"
                        }

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
@permission_classes([IsAppointmentParticipantPermission])
def get_zoom_meeting_info(request, appointment_id):
    """
    Get Zoom meeting information for a specific appointment
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
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


class ExpertAppointmentsForClientView(generics.ListAPIView):
    """
    Get expert's appointments within a date range for clients
    Only accessible by users with 'client' role
    Returns only essential appointment info: id, date, time, status
    """
    permission_classes = [IsAppointmentClientPermission]
    serializer_class = ExpertAppointmentSummarySerializer

    def list(self, request, *args, **kwargs):
        user = self.request.user

        expert_id = self.kwargs.get('expert_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        # Parametre kontrolü
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date ve end_date parametreleri zorunludur'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Tarih formatı YYYY-MM-DD olmalıdır'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if start_date > end_date:
            return Response(
                {'error': 'start_date, end_date\'den büyük olamaz'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = Appointment.objects.filter(
            expert_id=expert_id,
            date__range=[start_date, end_date],
            is_deleted=False
        ).order_by('date', 'time')

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'expert_id': self.kwargs.get('expert_id'),
            'start_date': request.query_params.get('start_date'),
            'end_date': request.query_params.get('end_date'),
            'appointments': serializer.data
        })
