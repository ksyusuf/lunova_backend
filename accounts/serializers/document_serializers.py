# accounts/serializers/document_serializers.py

from rest_framework import serializers
from accounts.models import Document, DocumentType


class DocumentSerializer(serializers.ModelSerializer):
    """
    Kullanıcıların yüklediği belgeleri (profil fotoğrafı, diploma, vb.)
    yönetmek için temel serializer.
    """
    
    filename = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "type",
            "file", # burası dosyanın tam dizinini dönüyor. böyle olmamalı. sadece kullanıcı id'si hariç sonrasını dönmeli.
            "filename",
            "updated_at",
            "verified",
            'verified_at',
        ]
        read_only_fields = ["id", "uploaded_at", "verified", "filename",]
        
    def get_filename(self, obj):
        # obj.file.name -> experts/2/profile_photos/noreply-logo.jpg
        # split('/') ile sadece son kısmı alıyoruz
        return obj.file.name.split('/')[-1]

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

        # Tekil olması gereken belge tipleri
        single_instance_types = [DocumentType.PROFILE_PHOTO]

        if doc_type in single_instance_types:
            existing = Document.objects.filter(user=user, type=doc_type).first()
            if existing:
                # Güncelleme mantığı — yeni dosya ile eskisini değiştir
                # şimdilik sadece profil fotoğrafı için çalışır.
                existing.file = validated_data.get("file", existing.file)
                existing.save(update_fields=["file"])
                return existing

        # Çoklu belge türleri için normal create
        validated_data["user"] = user
        return super().create(validated_data)

