from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            raw_token = request.COOKIES.get('access_token')
        else:
            raw_token = self.get_raw_token(header)
        
        if raw_token is None:
            return None
        
        try:
            # Token'ı validate et
            validated_token = self.get_validated_token(raw_token)
            
            # Token blacklist kontrolü yap - bu çok önemli
            if BlacklistedToken.objects.filter(token__jti=validated_token['jti']).exists():
                return None  # Blacklist'te varsa authentication başarısız
            
            return self.get_user(validated_token), validated_token
            
        except Exception:
            return None 