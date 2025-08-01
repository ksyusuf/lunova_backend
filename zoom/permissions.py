from rest_framework import permissions


class IsExpertPermission(permissions.BasePermission):
    """
    Sadece uzman rolündeki kullanıcıların erişimine izin verir.
    """
    
    def has_permission(self, request, view):
        # Kullanıcı giriş yapmış mı kontrol et
        if not request.user.is_authenticated:
            return False
        
        # Kullanıcının uzman rolünde olup olmadığını kontrol et
        # Burada User modelindeki role field'ını kontrol ediyoruz
        return hasattr(request.user, 'role') and request.user.role == 'expert' 