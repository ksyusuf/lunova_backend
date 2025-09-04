from django.urls import path
from .views import ExpertRegisterView, ClientRegisterView, AdminRegisterView, LoginView, LogoutView, MeView

urlpatterns = [
    path('register/expert/', ExpertRegisterView.as_view(), name='register_expert'),
    path('register/client/', ClientRegisterView.as_view(), name='register_client'),
    path('register/admin/', AdminRegisterView.as_view(), name='register_admin'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
]
