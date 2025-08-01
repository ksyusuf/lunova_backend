from rest_framework import permissions


class IsExpertOrReadOnlyPermission(permissions.BasePermission):
    """
    GET istekleri için herkes, POST/PUT/DELETE için sadece uzmanlar.
    """
    
    def has_permission(self, request, view):
        # GET istekleri için herkes erişebilir
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # POST/PUT/DELETE için sadece uzmanlar
        return hasattr(request.user, 'role') and request.user.role == 'expert'


class IsAppointmentParticipantPermission(permissions.BasePermission):
    """
    Randevuya dahil olan kullanıcıların erişimine izin verir.
    """
    
    def has_object_permission(self, request, view, obj):
        # Randevuya dahil olan kullanıcılar (expert veya client)
        return obj.expert == request.user or obj.client == request.user


class IsAppointmentExpertPermission(permissions.BasePermission):
    """
    Sadece randevunun uzmanının erişimine izin verir.
    """
    
    def has_object_permission(self, request, view, obj):
        # Sadece randevunun uzmanı
        return obj.expert == request.user 