# accounts/serializers/document_serializers.py

from rest_framework import serializers
from accounts.models import Document, DocumentType
from django.urls import reverse


class DocumentSerializer(serializers.ModelSerializer):
    """
    Kullanıcıların yüklediği belgeleri (profil fotoğrafı, diploma, vb.)
    yönetmek için temel serializer.
    """
    
    file = serializers.FileField(write_only=True, required=True)
    filename = serializers.SerializerMethodField()
    access_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "uid",
            "type",
            "file",
            "filename",
            "access_url",
            "updated_at",
            "verified",
            'verified_at',
        ]
        read_only_fields = ["uploaded_at", "verified", "filename"]
        

    def get_filename(self, obj):
        if obj.file:  # file None değilse
            return obj.file.name.split('/')[-1]
        return None
    
    def get_access_url(self, obj):
        request = self.context.get('request')
        if request is None:
            return None

        # Dosya kaydı yoksa hiç URL üretme
        if not obj.file or not obj.file.name:
            return None

        # Filename boşsa yine None dön
        filename = self.get_filename(obj)
        if not filename:
            return None

        # URL üret
        return request.build_absolute_uri(
            reverse("document_retrieve") +
            f"?uid={obj.uid}&type={obj.type}&filename={filename}"
        )

    def validate_type(self, value):
        """
        Yalnızca geçerli belge tiplerinin yüklenmesini sağlar.
        """
        valid_types = [choice[0] for choice in DocumentType.choices]
        if value not in valid_types:
            raise serializers.ValidationError("Geçersiz belge tipi.")
        return value

    def validate_file(self, value):
        """
        Dosya boyutu veya format kontrolü (isteğe bağlı).
        Örneğin 10MB sınırı ve sadece PDF/JPG.
        """
        max_size_mb = 10
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError("Dosya boyutu 10 MB'tan büyük olamaz.")
        
        allowed_types = ["image/jpeg", "image/png", "application/pdf"]
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Yalnızca JPG, PNG veya PDF dosyaları yüklenebilir.")
        
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        doc_type = validated_data.get("type")
        uploaded_file = validated_data.get("file")

        single_instance_types = [DocumentType.PROFILE_PHOTO]

        if doc_type in single_instance_types:
            document, created = Document.objects.get_or_create(
                user=user,
                type=doc_type,
                defaults={"file": uploaded_file}
            )
            if not created and uploaded_file:
                if document.file:
                    document.file.delete(save=False)
                document.file = uploaded_file
                document.save()
            return document

        document = Document.objects.create(
            user=user,
            type=doc_type,
            file=uploaded_file
        )
        return document
