from django.urls import path
from .views import (
    AppointmentListView,
    ExpertAppointmentCreateView,
    ClientAppointmentRequestView,
    AppointmentDetailView,
    get_user_appointments,
    confirm_appointment,
    get_zoom_meeting_info,
    approve_appointment,
    cancel_request_appointment,
    cancel_confirm_appointment
)

app_name = 'appointments'

urlpatterns = [
    # Listeleme
    path('', AppointmentListView.as_view(), name='appointment_list'),
    path('user/', get_user_appointments, name='user_appointments'),
    
    # Randevu oluşturma (ayrı endpoint'ler)
    path('expert/create/', ExpertAppointmentCreateView.as_view(), name='expert_appointment_create'),
    path('client/request/', ClientAppointmentRequestView.as_view(), name='client_appointment_request'),
    
    # Randevu detay ve işlemler
    path('<int:pk>/', AppointmentDetailView.as_view(), name='appointment_detail'),
    path('<int:appointment_id>/confirm/', confirm_appointment, name='confirm_appointment'),
    path('<int:appointment_id>/approve/', approve_appointment, name='approve_appointment'),
    path('<int:appointment_id>/cancel-request/', cancel_request_appointment, name='cancel_request_appointment'),
    path('<int:appointment_id>/cancel-confirm/', cancel_confirm_appointment, name='cancel_confirm_appointment'),
    path('<int:appointment_id>/meeting-info/', get_zoom_meeting_info, name='meeting_info'),
]