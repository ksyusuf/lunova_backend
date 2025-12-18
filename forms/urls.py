from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FormListView, FormDetailView, FormSubmitView, UserResponsesView, FormResponseDetailView
)

app_name = 'forms'

urlpatterns = [
    # Client endpoints
    path('', FormListView.as_view(), name='forms_list'),
    path('<int:form_id>/', FormDetailView.as_view(), name='form_detail'),
    path('submit/', FormSubmitView.as_view(), name='submit_form'),
    path('my-responses/', UserResponsesView.as_view(), name='user_responses'),
    path('responses/<int:response_id>/', FormResponseDetailView.as_view(), name='response_detail'),
]
