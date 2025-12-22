# accounts/serializers/base_update_serializer.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import GenderChoices
from rest_framework import serializers
from accounts.models import (
    ExpertProfile, ClientProfile, Language, AddictionType
    # Diğer Foreign Key/M2M modellerini de eklemeyi unutmayın
)
from .document_serializers import DocumentSerializer

User = get_user_model()


class BaseUserUpdateSerializer(serializers.ModelSerializer):
    """
    User modelindeki temel, güncellenebilir alanları yönetir.
    Diğer profil güncelleme serializer'ları içinde nested olarak kullanılır.
    """

    gender = serializers.CharField(required=False, allow_null=True) 
    # Not: birth_date, phone_number, country gibi alanlar User modelinde null/blank=True olduğu varsayılır.

    class Meta:
        model = User
        fields = [
            'first_name', 
            'last_name', 
            'birth_date', 
            'gender', 
            'phone_number', 
            'country'
        ]
        extra_kwargs = {
            'phone_number': {'required': False},
            'country': {'required': False},
            'birth_date': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate_gender(self, value):
        if value is not None and value not in [choice.value for choice in GenderChoices]:
            raise serializers.ValidationError('Geçersiz cinsiyet değeri.')
        return value
    

class ExpertProfileUpdateSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(source="user.documents", many=True, read_only=True)
    user_data = BaseUserUpdateSerializer(source='user', required=False)
    languages = serializers.SlugRelatedField(
        many=True,
        slug_field='code',
        queryset=Language.objects.all(), 
        required=False 
    )

    class Meta:
        model = ExpertProfile
        fields = [
            "about", "title", "experience_years", "license_number", 
            "institution", "services", "specializations", "languages", 
            "approach_methods", "target_groups", "session_types", 
            "session_price", "currency", "appointment_duration", 
            "free_first_session", "video_intro_url", "availability_status", 
            "university", "degree_level", "major", "documents",
            "user_data",
        ]
        read_only_fields = ["user", "approval_status", "rating_average", "rating_count"]

    def validate(self, attrs):
        allowed_fields = set(self.Meta.fields)
        received_fields = set(self.initial_data.keys())

        # user_data nested kontrolü hariç diğer tüm key'leri kontrol et
        invalid_fields = received_fields - allowed_fields
        if invalid_fields:
            raise serializers.ValidationError({
                "detail": f"Geçersiz alan(lar): {', '.join(invalid_fields)}"
            })

        return super().validate(attrs)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        user_instance = instance.user

        if user_data is not None:
            user_serializer = BaseUserUpdateSerializer(
                instance=user_instance, 
                data=user_data, 
                partial=True 
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        instance = super().update(instance, validated_data)
        return instance



class ClientProfileUpdateSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(source="user.documents", many=True, read_only=True)
    user_data = BaseUserUpdateSerializer(source='user', required=False)
    substances_used = serializers.PrimaryKeyRelatedField(
        queryset=AddictionType.objects.all(), 
        many=True, 
        required=False
    )

    class Meta:
        model = ClientProfile
        fields = [
            "support_goal",
            "received_service_before",
            "substances_used",
            "onboarding_complete",
            "is_active_in_treatment",
            "documents",
            "user_data",
        ]
        read_only_fields = ["user", "expert"]

    def validate(self, attrs):
        allowed_fields = set(self.Meta.fields)
        received_fields = set(self.initial_data.keys())

        invalid_fields = received_fields - allowed_fields
        if invalid_fields:
            raise serializers.ValidationError({
                "detail": f"Geçersiz alan(lar): {', '.join(invalid_fields)}"
            })

        return super().validate(attrs)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None) 
        user_instance = instance.user

        if user_data is not None:
            user_serializer = BaseUserUpdateSerializer(
                instance=user_instance, 
                data=user_data, 
                partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        instance = super().update(instance, validated_data)
        return instance
