from rest_framework import serializers
from accounts.models import Document, DocumentType
from accounts.storage import storage
from django.db import transaction, IntegrityError


class DocumentSerializer(serializers.ModelSerializer):
    """
    Presigned upload tamamlandıktan sonra
    document kaydını finalize eder.
    """

    file_key = serializers.CharField(write_only=True)
    access_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Document
        fields = [
            "uid",
            "type",
            "file_key",
            "original_filename",
            "is_primary",
            "access_url",
            "uploaded_at",
            "updated_at",
            "verified",
            "verified_at",
        ]
        read_only_fields = [
            "uploaded_at",
            "updated_at",
            "verified",
            "verified_at",
        ]

    # -------- READ --------
    
    def get_access_url(self, obj):
        """
        Dosya erişimi için signed GET URL üretir.
        # todo: obje bulunamadığı zaman obje bulunamadı hatasını uygun şekilde döndürmeliyiz.
        """
        request = self.context.get("request")
        user = request.user if request else None

        if not user or obj.user_id != user.id:
            return None

        if not obj.is_current:
            return None

        try:
            return storage.presign_download(
                key=obj.file_key,
                expires=3600
            )
        except Exception as exc:
            # storage ile db tutarsız → sessizce yok say
            return None


    # -------- VALIDATION --------

    def validate_type(self, value):
        valid_types = [c[0] for c in DocumentType.choices]
        if value not in valid_types:
            raise serializers.ValidationError("Geçersiz belge tipi.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        doc_type = attrs.get("type")

        # Aynı tipten max 3
        count = Document.objects.filter(user=user, type=doc_type, is_current=True).count()
        if count >= 3 and doc_type != DocumentType.PROFILE_PHOTO:
            raise serializers.ValidationError({
                "type": f"Aynı tipte ({doc_type}) en fazla 3 dosya yükleyebilirsiniz."
            })

        return attrs

    # -------- CREATE --------

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        file_key = validated_data.pop("file_key")
        original_filename = validated_data["original_filename"]
        doc_type = validated_data["type"]
        is_primary = validated_data.get("is_primary", False)


        existing = Document.objects.filter(file_key=file_key).first()
        
        if existing:
            if existing.user_id != user.id:
                raise serializers.ValidationError({
                    "file_key": "Bu dosya anahtarı size ait değil."
                })

            raise serializers.ValidationError({
                "file_key": (
                    "Bu dosya daha önce yüklenmiş. "
                    "Yeni bir dosya yüklemek için tekrar upload başlatmalısınız."
                )
            })

    
        try:
            with transaction.atomic():

                single_instance_types = [DocumentType.PROFILE_PHOTO]

                # Profil foto
                if doc_type in single_instance_types:
                    existing_doc = Document.objects.filter(
                        user=user,
                        type=doc_type,
                        is_current=True
                    ).first()

                    if existing_doc:
                        storage.delete(existing_doc.file_key)

                        existing_doc.file_key = file_key
                        existing_doc.original_filename = original_filename
                        existing_doc.is_primary = True
                        existing_doc.save()
                        return existing_doc

                # Normal doküman
                return Document.objects.create(
                    user=user,
                    original_filename=original_filename,
                    file_key=file_key,
                    type=doc_type,
                    is_primary=is_primary
                )
                
        except IntegrityError:
            # race condition fallback
            return Document.objects.get(file_key=file_key)