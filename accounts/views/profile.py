from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound
from accounts.models import Document, ExpertProfile, ClientProfile, UserRole
from django.db.models import Prefetch
from accounts.serializers.profile_update_serializers import (
    ExpertProfileUpdateSerializer,
    ClientProfileUpdateSerializer,
)
from accounts.permissions import IsOwnerProfile
from accounts.serializers.profileSerializers import ClientProfileSerializer, ExpertProfileSerializer


class ProfileView(RetrieveUpdateAPIView):
    """
    Tek endpoint üzerinden kullanıcı rolüne göre profil bilgilerini getirir ve günceller.
    /profile/
    """
    permission_classes = [IsAuthenticated, IsOwnerProfile]

    def get_object(self):
        user = self.request.user
        
        active_documents = Document.objects.filter(is_current=True)
        prefetch = Prefetch(
            "user__documents", 
            queryset=active_documents,
        )
        # 'user__documents' ifadesi: Profile -> User -> Documents yolunu izler

        try:
            if user.role == UserRole.EXPERT:
                return ExpertProfile.objects.prefetch_related(prefetch).get(user=user)
            elif user.role == UserRole.CLIENT:
                return ClientProfile.objects.prefetch_related(prefetch).get(user=user)
        except (ExpertProfile.DoesNotExist, ClientProfile.DoesNotExist):
            raise NotFound("Profil bulunamadı.")

        raise PermissionDenied("Bu endpoint sadece uzman ve danışan kullanıcılar içindir.")

    def get_serializer_class(self):
        user = self.request.user

        # READ
        if self.request.method == "GET":
            if user.role == UserRole.EXPERT:
                return ExpertProfileSerializer
            elif user.role == UserRole.CLIENT:
                return ClientProfileSerializer
            else:
                raise PermissionDenied("Bu endpoint sadece uzman ve danışan kullanıcılar içindir.")
            
        # UPDATE
        if self.request.method in ("PUT", "PATCH"):
            if user.role == UserRole.EXPERT:
                return ExpertProfileUpdateSerializer
            elif user.role == UserRole.CLIENT:
                return ClientProfileUpdateSerializer

        raise PermissionDenied("Bu endpoint sadece uzman ve danışan kullanıcılar içindir.")
