from django.urls import path
from . import views

app_name = 'zoom'

urlpatterns = [
    # Zoom meeting endpoints
    path('meetings/', views.create_zoom_meeting, name='create_meeting'),
] 