from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from accounts.models import (UserRole,
                             AdminProfile,
                             ExpertProfile,
                             ClientProfile,
                             AddictionType,
                             University,
                             GenderChoices,
                             EmergencyContact)

User = get_user_model()


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = []


class ExpertListSerializer(serializers.ModelSerializer):
    """Simplified serializer for expert listing with basic profile info"""
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    profile_photo = serializers.ImageField(source='user.profile_photo', read_only=True)
    gender = serializers.CharField(source='user.gender', read_only=True)
    services = serializers.SerializerMethodField()

    class Meta:
        model = ExpertProfile
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'profile_photo',
            'university',
            'about',
            'approval_status',
            'gender',
            'services',
        ]

    def get_services(self, obj):
        """Return list of service names"""
        return [service.name for service in obj.services.all()]


class AddictionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddictionType
        fields = ['id', 'name', 'description', 'is_active']


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "name",
            "phone_number",
            "relationship",
            "is_primary",
        ]


# -----------------------------
# Base Register Serializer
# -----------------------------
class BaseRegisterSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(write_only=True, required=True)
    id_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    country = serializers.CharField(required=False, default="TR")
    national_id = serializers.CharField(required=False, allow_blank=True)
    birth_date = serializers.DateField(required=True)
    gender = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Şifreler eşleşmiyor."})

        for field in ['first_name', 'last_name', 'email', 'phone_number']:
            if not attrs.get(field):
                raise serializers.ValidationError({field: f"{field.replace('_',' ').capitalize()} zorunludur."})

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Bu email adresi ile kayıtlı bir kullanıcı zaten var."})

        country = attrs.get("country")
        id_number = attrs.get("id_number")
        national_id = attrs.get("national_id")

        # Turkey: id_number (TC Kimlik) required
        if country == "TR":
            attrs['timezone'] = "Europe/Istanbul"
            if not id_number:
                raise serializers.ValidationError({"id_number": "Türkiye için TC Kimlik zorunludur."})
            if not id_number.isdigit() or len(id_number) != 11:
                raise serializers.ValidationError({"id_number": "TC Kimlik numarası 11 haneli ve sadece rakamlardan oluşmalıdır."})

            # Duplicate check on User now that id_number lives on User
            if User.objects.filter(id_number=id_number).exists():
                raise serializers.ValidationError({"id_number": "Bu TC Kimlik numarası ile kayıtlı bir kullanıcı zaten var."})

        # International users: national_id required
        else:
            attrs.setdefault('timezone', 'UTC')
            if not national_id:
                raise serializers.ValidationError({"national_id": f"{country} için kimlik numarası zorunludur."})

        gender_value = attrs.get('gender')
        if gender_value is not None and gender_value not in [choice.value for choice in GenderChoices]:
            raise serializers.ValidationError({'gender': 'Geçersiz cinsiyet.'})

        return attrs


# -----------------------------
# Expert Register Serializer
# -----------------------------
class ExpertRegisterSerializer(BaseRegisterSerializer):
    university_id = serializers.IntegerField(write_only=True, required=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # University kontrolü
        try:
            attrs['university'] = University.objects.get(id=attrs.pop('university_id'))
        except University.DoesNotExist:
            raise serializers.ValidationError({'university_id': 'Geçersiz üniversite IDsi.'})
        return attrs

    def create(self, validated_data):
        university = validated_data.pop('university')

        # User oluşturma
        password = validated_data.pop('password')
        validated_data.pop('password2', None)
        user = User(**validated_data, role=UserRole.EXPERT)
        user.set_password(password)
        user.save()

        ExpertProfile.objects.create(
            user=user,
            university=university
        )

        return user

    def to_representation(self, instance):
        """Control what gets returned in the response"""
        return {
            'email': instance.email,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'message': 'Expert user registered successfully'
        }


# -----------------------------
# Client Register Serializer
# -----------------------------
class ClientRegisterSerializer(BaseRegisterSerializer):
    support_goal = serializers.CharField(required=False, allow_blank=True)
    received_service_before = serializers.BooleanField(default=False)
    substances_used = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=AddictionType.objects.all()),
        required=True,
        allow_empty=False
    )

    def create(self, validated_data):
        substances_used = validated_data.pop('substances_used', [])
        support_goal = validated_data.pop('support_goal', '')
        received_service_before = validated_data.pop('received_service_before', False)
        password = validated_data.pop('password')
        validated_data.pop('password2', None)

        # User oluştur
        user = User(**validated_data, role=UserRole.CLIENT)
        user.set_password(password)
        user.save()

        # ClientProfile oluştur
        client_profile = ClientProfile.objects.create(
            user=user,
            support_goal=support_goal,
            received_service_before=received_service_before
        )
        if substances_used:
            client_profile.substances_used.set(substances_used)

        return user

    def to_representation(self, instance):
        """Control what gets returned in the response"""
        return {
            'id': instance.id,
            'email': instance.email,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'role': instance.role,
            'username': instance.username,
            'message': 'Client user registered successfully'
        }

class ClientListSerializer(serializers.ModelSerializer):
    """Simplified serializer for client listing with basic profile info"""
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    profile_photo = serializers.ImageField(source='user.profile_photo', read_only=True)
    gender = serializers.CharField(source='user.gender', read_only=True)
    substances_used = serializers.SerializerMethodField()
    birth_date = serializers.DateField(source='user.birth_date', read_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'profile_photo',
            'gender',
            'birth_date',
            'substances_used',
            'support_goal',
            'received_service_before',
            'onboarding_complete',
            'is_active_in_treatment',
        ]

    def get_substances_used(self, obj):
        """Return list of addiction type names"""
        return [addiction.name for addiction in obj.substances_used.all()]

# -----------------------------
# Admin Register Serializer
# -----------------------------
class AdminRegisterSerializer(BaseRegisterSerializer):

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # Admin-specific validations can be added here
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')

        # Extract only User model fields
        user_data = {
            'username': validated_data.get('email'),
            'email': validated_data.get('email'),
            'first_name': validated_data.get('first_name'),
            'last_name': validated_data.get('last_name'),
            'role': UserRole.ADMIN
        }
        
        user = User(**user_data)
        user.set_password(password)
        user.save()

        AdminProfile.objects.create(user=user)

        return user

    def to_representation(self, instance):
        """Control what gets returned in the response"""
        return {
            'id': instance.id,
            'email': instance.email,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'role': instance.role,
            'username': instance.username,
            'message': 'Admin user registered successfully'
        }


# -----------------------------
# Login Serializer
# -----------------------------
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
        user = authenticate(email=user.email, password=password)
        if not user:
            raise serializers.ValidationError(_("Geçersiz e-posta veya şifre."))
        data['user'] = user
        return data


# -----------------------------
# Password Reset Serializers
# -----------------------------
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Şifreler eşleşmiyor."})
        return attrs
