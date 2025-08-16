from rest_framework import permissions


class IsExpertOrClientForCreatePermission(permissions.BasePermission):
    """
    GET istekleri için herkes, POST için uzmanlar ve danışanlar, PUT/DELETE için sadece uzmanlar.
    """
    
    def has_permission(self, request, view):
        # GET istekleri için herkes erişebilir
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # POST için uzmanlar ve danışanlar
        if request.method == 'POST':
            return (hasattr(request.user, 'role') and
                   request.user.role in ['expert', 'client'])
        
        # PUT/DELETE için sadece uzmanlar
        return hasattr(request.user, 'role') and request.user.role == 'expert'


class IsAppointmentParticipantPermission(permissions.BasePermission):
    """
    Randevuya dahil olan kullanıcıların erişimine izin verir.
    """
    
    def has_permission(self, request, view):
        # Kimlik doğrulanmış kullanıcılar erişebilir
        return request.user.is_authenticated
    
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


class IsAppointmentClientPermission(permissions.BasePermission):
    """
    Sadece randevunun danışanının erişimine izin verir.
    """
    
    def has_object_permission(self, request, view, obj):
        # Sadece randevunun danışanı
        return obj.client == request.user