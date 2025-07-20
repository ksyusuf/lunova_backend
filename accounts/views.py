from rest_framework import generics
from .serializers import RegisterSerializer
from .serializers import LoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError



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

        return Response({
            "refresh": refresh_token,
            "access": access_token,
            "username": user.username,
            "email": user.email,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Başarıyla çıkış yapıldı."}, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({"error": "Refresh token gönderilmedi."}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            return Response({"error": "Geçersiz veya süresi dolmuş token."}, status=status.HTTP_400_BAD_REQUEST)
