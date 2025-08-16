from django.urls import path
from . import views

app_name = 'forms'

urlpatterns = [
    # Form listesi
    path('', views.get_forms_list, name='forms_list'),
    
    # Form detayı
    path('<int:form_id>/', views.get_form_detail, name='form_detail'),
    
    # Form gönderimi
    path('submit/', views.submit_form, name='submit_form'),
    
    # Kullanıcı cevapları
    path('my-responses/', views.get_user_responses, name='user_responses'),
    
    # Cevap detayı
    path('responses/<int:response_id>/', views.get_form_response_detail, name='response_detail'),
]
