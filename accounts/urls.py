from django.urls import path
from .views.views import ExpertRegisterView, ClientRegisterView, AdminRegisterView, LoginView, LogoutView, MeView, ExpertListView, PasswordResetRequestView, PasswordResetConfirmView
from .views.profile import ProfileView
from .views.document_views import DocumentUploadView

urlpatterns = [
    path('register/expert/', ExpertRegisterView.as_view(), name='register_expert'),
    path('register/client/', ClientRegisterView.as_view(), name='register_client'),
    path('register/admin/', AdminRegisterView.as_view(), name='register_admin'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    path('experts/', ExpertListView.as_view(), name='expert_list'),
    
    path("profile/", ProfileView.as_view(), name="profile"),
    path("documents/upload/", DocumentUploadView.as_view(), name="document_upload"),

    # password reset enpoints
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
