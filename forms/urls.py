from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FormListView,
    FormDetailView, FormSubmitView,
    UserResponsesView,
    UserResponseDetailView,
    FormClientResponsesView,
    FormClientResponseDetailView
)

app_name = 'forms'

urlpatterns = [
    # Client endpoints
    path('', FormListView.as_view(), name='forms_list'),
    path('<int:form_id>/', FormDetailView.as_view(), name='form_detail'),
    
    path('submit/', FormSubmitView.as_view(), name='submit_form'),
    
    path('me/form-responses/', UserResponsesView.as_view(), name='user_responses'),
    
    path('me/form-responses/<int:response_id>/',
         UserResponseDetailView.as_view(),
         name='user_responses_detail'),
    
    
    path('clients/<int:client_id>/form-responses/',
         FormClientResponsesView.as_view(),
         name='clients_responses'),
    
    path('clients/<int:client_id>/form-responses/<int:response_id>/',
         FormClientResponseDetailView.as_view(),
         name='clients_response_detail'),
]
