from django.urls import path
from . import views

app_name = 'availability'

urlpatterns = [
    # Weekly availability endpoints
    path('weekly/', views.WeeklyAvailabilityViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='weekly_availability'),
    
    path('weekly/<int:pk>/', views.WeeklyAvailabilityDetailView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='weekly_availability_detail'),
    
    # Availability exceptions endpoints
    path('exceptions/', views.AvailabilityExceptionViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='availability_exceptions'),
    
    path('exceptions/<int:pk>/', views.AvailabilityExceptionDetailView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='availability_exception_detail'),
    
    # Bulk operations
    path('weekly/bulk/', views.BulkWeeklyAvailabilityView.as_view(), name='bulk_weekly_availability'),
    path('exceptions/bulk/', views.BulkAvailabilityExceptionView.as_view(), name='bulk_availability_exceptions'),
    
    # Expert availability views
    path('expert/<int:expert_id>/', views.ExpertAvailabilityView.as_view(), name='expert_availability'),
    path('expert/<int:expert_id>/calendar/', views.expert_availability_calendar, name='expert_availability_calendar'),
    path('my-availability/', views.MyAvailabilityView.as_view(), name='my_availability'),
]
