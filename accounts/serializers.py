from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from accounts.models import UserRole

from .models import AdminProfile, ExpertProfile, ClientProfile

User = get_user_model()


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = []


class ExpertProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpertProfile
        fields = [
            'tc_kimlik',
            'diploma_dosyasi',
            'universite',
            'gsm_no',
            'uzmanlik_alani',
            'hakkinda',
            'onay_durumu',
            'profil_fotografi',
        ]


class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = [
            'tc_kimlik',
            'daha_once_hizmet_aldi_mi',
            'kullandigi_maddeler',
            'bagimlilik_turu',
            'destek_amaci',
            'yas',
            'cinsiyet',
            'gsm_no',
            'profil_fotografi',
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=UserRole)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    gsm_no = serializers.CharField(write_only=True, required=True)
    tc_kimlik = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'password2', 'role', 'gsm_no', 'tc_kimlik')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Şifreler eşleşmiyor."})

        if not attrs.get('first_name'):
            raise serializers.ValidationError({"first_name": "İsim zorunludur."})
        if not attrs.get('last_name'):
            raise serializers.ValidationError({"last_name": "Soyisim zorunludur."})
        if not attrs.get('email'):
            raise serializers.ValidationError({"email": "Email zorunludur."})
        if not attrs.get('gsm_no'):
            raise serializers.ValidationError({"gsm_no": "GSM zorunludur."})
        if not attrs.get('tc_kimlik'):
            raise serializers.ValidationError({"tc_kimlik": "TC Kimlik numarası zorunludur."})
        # Email benzersiz mi?
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Bu email adresi ile kayıtlı bir kullanıcı zaten var."})
        # TC Kimlik benzersiz mi? (hem Expert hem Client için kontrol)
        if ExpertProfile.objects.filter(tc_kimlik=attrs['tc_kimlik']).exists() or ClientProfile.objects.filter(tc_kimlik=attrs['tc_kimlik']).exists():
            raise serializers.ValidationError({"tc_kimlik": "Bu TC Kimlik numarası ile kayıtlı bir kullanıcı zaten var."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')
        gsm_no = validated_data.pop('gsm_no')
        tc_kimlik = validated_data.pop('tc_kimlik')
        role = validated_data.get('role')
        email = validated_data.get('email')
        user = User(username=email, **validated_data)
        user.set_password(password)
        user.save()

        if role == UserRole.ADMIN:
            AdminProfile.objects.create(user=user)
        elif role == UserRole.EXPERT:
            ExpertProfile.objects.create(user=user, tc_kimlik=tc_kimlik, gsm_no=gsm_no)
        elif role == UserRole.CLIENT:
            ClientProfile.objects.create(user=user, tc_kimlik=tc_kimlik, gsm_no=gsm_no)

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("Geçersiz e-posta veya şifre."))
        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError(_("Geçersiz e-posta veya şifre."))
        data['user'] = user
        return data
