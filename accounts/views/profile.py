from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from accounts.models import ExpertProfile, ClientProfile, UserRole
from accounts.serializers.profile_update_serializers import (
    ExpertProfileUpdateSerializer,
    ClientProfileUpdateSerializer,
)
from accounts.permissions import IsOwnerProfile


class ProfileView(RetrieveUpdateAPIView):
    """
    Tek endpoint üzerinden kullanıcı rolüne göre profil bilgilerini getirir ve günceller.
    /profile/
    """

    permission_classes = [IsAuthenticated, IsOwnerProfile]

    def get_object(self):
        user = self.request.user

        if user.role == UserRole.EXPERT:
            return ExpertProfile.objects.get(user=user)
        elif user.role == UserRole.CLIENT:
            return ClientProfile.objects.get(user=user)

        raise PermissionDenied("Bu endpoint sadece uzman ve danışan kullanıcılar içindir.")

    def get_serializer_class(self):
        user = self.request.user

        if user.role == UserRole.EXPERT:
            return ExpertProfileUpdateSerializer
        elif user.role == UserRole.CLIENT:
            return ClientProfileUpdateSerializer

        raise PermissionDenied("Bu endpoint sadece uzman ve danışan kullanıcılar içindir.")
