from django.urls import path
from . import views

app_name = 'availability'

urlpatterns = [
    # My availability (weekly + exceptions combined)
    path('', views.MyAvailabilityView.as_view(), name='my_availability'),

    # Weekly availability (list + bulk update/delete)
    path('weekly/', views.WeeklyAvailabilityView.as_view(), name='weekly_availability'),

    # Availability exceptions (list + bulk update/delete)
    path('exceptions/', views.AvailabilityExceptionView.as_view(), name='availability_exceptions'),

    # Expert and public views
    path('expert/<int:expert_id>/', views.ExpertAvailabilityView.as_view(), name='expert_availability'),
    path('available-experts/', views.AvailableExpertsByCategoryView.as_view(), name='available_experts'),
]

