from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from accounts.models import UserRole, AdminProfile, ExpertProfile, ClientProfile, AddictionType

User = get_user_model()


# -----------------------------
# Profile Serializers
# -----------------------------

class BaseProfileSerializer(serializers.ModelSerializer):
    id_number = serializers.CharField(source='user.id_number', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    profile_photo = serializers.ImageField(source='user.profile_photo', read_only=True)
    country = serializers.CharField(source='user.country', read_only=True)
    national_id = serializers.CharField(source='user.national_id', read_only=True)
    gender = serializers.IntegerField(source='user.gender_id', read_only=True)
    birth_date = serializers.DateField(source='user.birth_date', read_only=True)

class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = []


class ExpertProfileSerializer(BaseProfileSerializer):
    class Meta:
        model = ExpertProfile
        fields = [
            'id_number',
            'degree_file',
            'university',
            'phone_number',
            'about',
            'approval_status',
            'profile_photo',
            'services',
            'country',
            'national_id',
            'gender',
            'birth_date',
        ]


class AddictionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddictionType
        fields = ['id', 'name', 'description', 'is_active']


class ClientProfileSerializer(BaseProfileSerializer):
    substances_used = AddictionTypeSerializer(many=True, read_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            'id_number',
            'received_service_before',
            'substances_used',
            'support_goal',
            'birth_date',
            'gender',
            'phone_number',
            'profile_photo',
            'country',
            'national_id',
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
    birth_date = serializers.DateField(required=False)
    gender_id = serializers.IntegerField(required=False, allow_null=True)
    profile_photo = serializers.ImageField(required=False)

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

        return attrs


# -----------------------------
# Expert Register Serializer
# -----------------------------
class ExpertRegisterSerializer(BaseRegisterSerializer):
    university = serializers.CharField(required=True)
    about = serializers.CharField(required=False, allow_blank=True)
    degree_file = serializers.FileField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # Expert-specific validations can be added here
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')
        phone_number = validated_data.pop('phone_number')
        id_number = validated_data.pop('id_number', None)
        university = validated_data.pop('university')
        about = validated_data.pop('about', '')
        degree_file = validated_data.pop('degree_file', None)
        country = validated_data.pop('country', "TR")
        national_id = validated_data.pop('national_id', "")
        birth_date = validated_data.pop('birth_date', None)
        gender_id = validated_data.pop('gender_id', None)
        profile_photo = validated_data.pop('profile_photo', None)

        # Extract only User model fields
        user_data = {
            'username': validated_data.get('email'),
            'email': validated_data.get('email'),
            'first_name': validated_data.get('first_name'),
            'last_name': validated_data.get('last_name'),
            'role': UserRole.EXPERT
        }
        
        user = User(**user_data)
        user.phone_number = phone_number
        user.id_number = id_number
        user.country = country
        user.national_id = national_id
        user.birth_date = birth_date
        if gender_id is not None:
            user.gender_id = gender_id
        if profile_photo is not None:
            user.profile_photo = profile_photo
        user.set_password(password)
        user.save()

        ExpertProfile.objects.create(
            user=user,
            university=university,
            about=about,
            degree_file=degree_file,
        )

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
            'message': 'Expert user registered successfully'
        }


# -----------------------------
# Client Register Serializer
# -----------------------------
class ClientRegisterSerializer(BaseRegisterSerializer):
    birth_date = serializers.DateField(required=False)
    gender_id = serializers.IntegerField(required=False, allow_null=True)
    support_goal = serializers.CharField(required=False, allow_blank=True)
    received_service_before = serializers.BooleanField(default=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # Client-specific validations can be added here
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')
        phone_number = validated_data.pop('phone_number')
        id_number = validated_data.pop('id_number', None)
        birth_date = validated_data.pop('birth_date', None)
        gender_id = validated_data.pop('gender_id', None)
        support_goal = validated_data.pop('support_goal', '')
        received_service_before = validated_data.pop('received_service_before', False)
        country = validated_data.pop('country', "TR")
        national_id = validated_data.pop('national_id', "")
        profile_photo = validated_data.pop('profile_photo', None)

        # Extract only User model fields
        user_data = {
            'username': validated_data.get('email'),
            'email': validated_data.get('email'),
            'first_name': validated_data.get('first_name'),
            'last_name': validated_data.get('last_name'),
            'role': UserRole.CLIENT
        }
        
        user = User(**user_data)
        user.phone_number = phone_number
        user.id_number = id_number
        user.country = country
        user.national_id = national_id
        user.birth_date = birth_date
        if gender_id is not None:
            user.gender_id = gender_id
        if profile_photo is not None:
            user.profile_photo = profile_photo
        user.set_password(password)
        user.save()

        ClientProfile.objects.create(
            user=user,
            support_goal=support_goal,
            received_service_before=received_service_before
        )

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
        phone_number = validated_data.pop('phone_number')
        id_number = validated_data.pop('id_number', None)
        country = validated_data.pop('country', "TR")
        national_id = validated_data.pop('national_id', "")

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
