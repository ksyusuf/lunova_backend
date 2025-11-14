from rest_framework.permissions import BasePermission


class IsOwnerProfile(BasePermission):
    """
    Kullanıcı yalnızca kendi profilini düzenleyebilir.
    """

    def has_object_permission(self, request, view, obj):
        return hasattr(obj, "user") and obj.user == request.user
