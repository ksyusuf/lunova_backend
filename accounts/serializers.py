from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import AdminProfile, ExpertProfile, ClientProfile

User = get_user_model()


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = []


class ExpertProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpertProfile
        fields = ['tc_kimlik']


class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ['tc_kimlik']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    # Profil alanları
    tc_kimlik = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'role', 'tc_kimlik')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Şifreler eşleşmiyor."})

        role = attrs.get('role')
        if role in ['expert', 'client'] and not attrs.get('tc_kimlik'):
            raise serializers.ValidationError({"tc_kimlik": "TC Kimlik numarası zorunludur."})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')
        tc_kimlik = validated_data.pop('tc_kimlik', None)
        role = validated_data.get('role')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Profil oluştur
        if role == 'admin':
            AdminProfile.objects.create(user=user)
        elif role == 'expert':
            ExpertProfile.objects.create(user=user, tc_kimlik=tc_kimlik)
        elif role == 'client':
            ClientProfile.objects.create(user=user, tc_kimlik=tc_kimlik)

        return user
