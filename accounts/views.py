from rest_framework import generics
from .serializers import RegisterSerializer
from .serializers import LoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


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
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        response = Response({
            "refresh": refresh_token,
            "access": access_token,
            "email": user.email,
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
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Response({"detail": "Başarıyla çıkış yapıldı."}, status=status.HTTP_205_RESET_CONTENT)
            # Cookie'leri expire et
            cookie_params = {
                'expires': 0,
                'path': '/',
            }
            # Ortam kontrolü: prod ise domain ekle
            if getattr(settings, 'ENVIRONMENT', '').lower() == 'production':
                cookie_params['domain'] = 'lunova.tr'
            response.set_cookie(
                key="access_token",
                value="",
                **cookie_params
            )
            response.set_cookie(
                key="refresh_token",
                value="",
                **cookie_params
            )
            return response
        except KeyError:
            return Response({"error": "Refresh token gönderilmedi."}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            return Response({"error": "Geçersiz veya süresi dolmuş token."}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": getattr(user, "role", None),
            "first_name": user.first_name,
            "last_name": user.last_name,
        }, status=status.HTTP_200_OK)
