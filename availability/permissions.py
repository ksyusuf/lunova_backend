from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission


class IsExpertWithProfile(permissions.BasePermission):
    """
    Kullanıcının uzman rolüne ve bir ExpertProfile nesnesine sahip olduğunu kontrol eder.
    """
    
    def has_permission(self, request, view):
        user = request.user
        if user.role != 'expert':
            raise ValidationError("Bu işlem yalnızca uzmanlar için geçerlidir.")
        if not hasattr(user, 'expertprofile'):
            raise ValidationError("Kullanıcının bir uzman profili yok.")
        return True


class IsExpertOrAuthenticatedReadOnly(permissions.BasePermission):
    """
    GET istekleri için kimlik doğrulaması yapılmış tüm kullanıcılar,
    diğer istekler için yalnızca uzmanlar erişebilir.
    """

    def has_permission(self, request, view):
        # SAFE_METHODS (GET, HEAD, OPTIONS) için kimlik doğrulaması yeterli
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Diğer istekler için uzman rolü kontrolü
        return hasattr(request.user, 'expertprofile')


class IsExpertPermission(BasePermission):
    """
    Allows access only to users with an expert profile.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'expertprofile')


class IsAvailabilityOwnerPermission(BasePermission):
    """
    Allows access only to the owner of the availability.
    """
    def has_object_permission(self, request, view, obj):
        return obj.expert == request.user.expertprofile


class IsExpertOrReadOnly(BasePermission):
    """
    Allows read-only access to authenticated users and full access to experts.
    """
    def has_permission(self, request, view):
        # Allow read-only access for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Allow full access for users with an expert profile
        return hasattr(request.user, 'expertprofile')
