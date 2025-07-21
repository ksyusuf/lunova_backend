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

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class LoginView(APIView):
    serializer_class = LoginSerializer

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
            "username": user.username,
            "email": user.email,
        }, status=status.HTTP_200_OK)
        # JWT'yi httpOnly cookie olarak ekle
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="None",
            secure=True,  # PROD: HTTPS zorunlu! Geliştirmede de True bırak, test için https kullan.
            # PROD: domain parametresi ekle (ör: .seninprojen.com) -> domain=".seninprojen.com",
            max_age=60*15,  # 15 dakika
            path="/"
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="None",
            secure=True,  # PROD: HTTPS zorunlu! Geliştirmede de True bırak, test için https kullan.
            # PROD: domain parametresi ekle (ör: .seninprojen.com) -> domain=".seninprojen.com",
            max_age=60*60*24*7,  # 7 gün
            path="/"
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
            response.set_cookie(
                key="access_token",
                value="",
                expires=0,
                path="/"
            )
            response.set_cookie(
                key="refresh_token",
                value="",
                expires=0,
                path="/"
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
        }, status=status.HTTP_200_OK)
