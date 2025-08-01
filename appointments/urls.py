from django.urls import path
from .views import (
    AppointmentListCreateView, 
    AppointmentDetailView,
    get_user_appointments,
    confirm_appointment,
    get_zoom_meeting_info
)

app_name = 'appointments'

urlpatterns = [
    path('', AppointmentListCreateView.as_view(), name='appointment_list_create'),
    path('<int:pk>/', AppointmentDetailView.as_view(), name='appointment_detail'),
    path('user/', get_user_appointments, name='user_appointments'),
    path('<int:appointment_id>/confirm/', confirm_appointment, name='confirm_appointment'),
    path('<int:appointment_id>/meeting-info/', get_zoom_meeting_info, name='meeting_info'),
]