from django.urls import path
from .views import (
    AppointmentListView,
    ExpertAppointmentCreateView,
    ClientAppointmentRequestView,
    AppointmentDetailView,
    get_zoom_meeting_info,
    ExpertAppointmentsForClientView,
)

app_name = 'appointments'

urlpatterns = [
    # Listeleme
    path('', AppointmentListView.as_view(), name='appointment_list'),
    
    # Randevu oluşturma (ayrı endpoint'ler)
    path('expert/create/', ExpertAppointmentCreateView.as_view(), name='expert_appointment_create'),
    path('client/request/', ClientAppointmentRequestView.as_view(), name='client_appointment_request'),
    
    # Randevu detay ve işlemler
    path('<int:pk>/', AppointmentDetailView.as_view(), name='appointment_detail'),
    path('<int:pk>/status/', AppointmentDetailView.as_view(), name='appointment_status_update'),
    path('<int:appointment_id>/meeting-info/', get_zoom_meeting_info, name='meeting_info'),

    # Expert appointments for clients
    path('experts/<int:expert_id>/appointments/', ExpertAppointmentsForClientView.as_view(), name='expert_appointments'),
]