from django.urls import path
from .views.views import ExpertRegisterView, ClientRegisterView, AdminRegisterView, LoginView, LogoutView, MeView, ExpertListView, ClientListView, PasswordResetRequestView, PasswordResetConfirmView
from .views.profile import ProfileView
from .views.document_views import DocumentListCreateView, DocumentPresignUploadView, DocumentDeleteView

urlpatterns = [
    path('register/expert/', ExpertRegisterView.as_view(), name='register_expert'),
    path('register/client/', ClientRegisterView.as_view(), name='register_client'),
    path('register/admin/', AdminRegisterView.as_view(), name='register_admin'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    path('experts/', ExpertListView.as_view(), name='expert_list'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    
    path("profile/", ProfileView.as_view(), name="profile"),
    
    path("documents/presign-upload/", DocumentPresignUploadView.as_view(), name="document-presign-upload"),
    path("documents/", DocumentListCreateView.as_view()),
    path("documents/<uuid:uid>/", DocumentDeleteView.as_view(), name="document-delete"),

    # password reset enpoints
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
