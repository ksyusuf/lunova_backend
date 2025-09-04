from rest_framework import generics
from .serializers import ExpertRegisterSerializer, ClientRegisterSerializer, AdminRegisterSerializer
from .serializers import LoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

User = get_user_model()


class ExpertRegisterView(generics.CreateAPIView):
    serializer_class = ExpertRegisterSerializer


class ClientRegisterView(generics.CreateAPIView):
    serializer_class = ClientRegisterSerializer


class AdminRegisterView(generics.CreateAPIView):
    serializer_class = AdminRegisterSerializer


class LoginView(APIView):
    serializer_class = LoginSerializer
    """
    POST /login/ endpointi artık email ve password bekler.
    {
        "email": "kullanici@ornek.com",
        "password": "sifre"
    }
    """
    def post(self, request):
        # Önce frontend tipini belirle
        frontend_type = request.META.get('HTTP_X_FRONTEND_TYPE', '')
        
        # Eğer header yoksa, referer header'ından kontrol et
        if not frontend_type:
            referer = request.META.get('HTTP_REFERER', '')
            
            # Expert frontend domain'lerini kontrol et
            expert_domains = [
                'expert.lunova.tr',
                'localhost:5173',  # Expert frontend dev port (Vite default)
                '127.0.0.1:5173',  # Localhost alternatif
            ]
            
            # Client frontend domain'lerini kontrol et
            client_domains = [
                'client.lunova.tr',
                'lunova.tr',  # Ana domain
                'localhost:5174',  # Client frontend dev port (farklı port)
                '127.0.0.1:5174',  # Localhost alternatif
            ]
            
            if any(domain in referer for domain in expert_domains):
                frontend_type = 'expert'
            elif any(domain in referer for domain in client_domains):
                frontend_type = 'client'
        
        is_expert_frontend = frontend_type == 'expert'
        is_client_frontend = frontend_type == 'client'
        
        # Email'e göre kullanıcıyı bul
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "detail": "Geçersiz e-posta veya şifre."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Rol kontrolü yap (sadece frontend tipi belirlenmişse)
        if is_expert_frontend and user.role == 'client':
            return Response({
                "detail": "Bu arayüz sadece uzmanlar için tasarlanmıştır. Lütfen danışan arayüzünü kullanın."
            }, status=status.HTTP_403_FORBIDDEN)
        
        if is_client_frontend and user.role == 'expert':
            return Response({
                "detail": "Bu arayüz sadece danışanlar için tasarlanmıştır. Lütfen uzman arayüzünü kullanın."
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Şimdi şifre kontrolü yap
        password = request.data.get('password')
        user = authenticate(email=user.email, password=password)
        if not user:
            return Response({
                "detail": "Geçersiz e-posta veya şifre."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normal login işlemi devam eder
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        response = Response({
            "refresh": refresh_token,
            "access": access_token,
            "email": user.email,
            "role": user.role,  # Role bilgisini de döndür
        }, status=status.HTTP_200_OK)
        # JWT'yi httpOnly cookie olarak ekle
        cookie_params = {
            'httponly': True,
            'samesite': 'None',
            'secure': True,
            'max_age': 60*15,
            'path': '/',
        }
        refresh_cookie_params = cookie_params.copy()
        refresh_cookie_params['max_age'] = 60*60*24*7

        # Ortam kontrolü: prod ise domain ekle
        if getattr(settings, 'ENVIRONMENT', '').lower() == 'production':
            cookie_params['domain'] = 'lunova.tr'
            refresh_cookie_params['domain'] = 'lunova.tr'

        response.set_cookie(
            key="access_token",
            value=access_token,
            **cookie_params
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            **refresh_cookie_params
        )
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token") or request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token bulunamadı."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Token'ı blacklist'e ekle
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Access token'ı da blacklist'e ekle (eğer varsa)
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header and auth_header.startswith('Bearer '):
                access_token = auth_header.split(' ')[1]
                try:
                    access_token_obj = RefreshToken(access_token)
                    access_token_obj.blacklist()
                except:
                    pass  # Access token blacklist edilemezse devam et
            
            response = Response({"detail": "Başarıyla çıkış yapıldı."}, status=status.HTTP_205_RESET_CONTENT)
            
            # Cookie'leri tamamen kaldır (expire yerine delete kullan)
            cookie_params = {
                'path': '/',
            }
            
            # Ortam kontrolü: prod ise domain ekle
            if getattr(settings, 'ENVIRONMENT', '').lower() == 'production':
                cookie_params['domain'] = 'lunova.tr'
            
            # Access token cookie'sini kaldır
            response.delete_cookie(
                key="access_token",
                **cookie_params
            )
            
            # Refresh token cookie'sini kaldır
            response.delete_cookie(
                key="refresh_token",
                **cookie_params
            )
            
            # Cookie'leri tamamen temizlemek için expire date ekle
            response.set_cookie(
                key="access_token",
                value="",
                expires="Thu, 01 Jan 1970 00:00:00 GMT",
                **cookie_params
            )
            response.set_cookie(
                key="refresh_token", 
                value="",
                expires="Thu, 01 Jan 1970 00:00:00 GMT",
                **cookie_params
            )
            
            return response
            
        except TokenError:
            return Response({"error": "Geçersiz veya süresi dolmuş token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Çıkış işlemi sırasında hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Logout'taki gibi refresh token kontrolü yap
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Kullanıcı bulunamadı."}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": getattr(user, "role", None),
            "first_name": user.first_name,
            "last_name": user.last_name,
        }, status=status.HTTP_200_OK)
