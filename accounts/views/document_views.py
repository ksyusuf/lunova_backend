# accounts/views/document_views.py
import logging
import uuid
from django.db import transaction
from accounts.serializers.document_serializers import DocumentSerializer
from accounts.models import Document, DocumentType
from accounts.storage import storage
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError  
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


permission_classes = [IsAuthenticated]
logger = logging.getLogger(__name__)

class DocumentListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.filter(
            user=self.request.user,
            is_current=True
        )

    def get_serializer_context(self):
        return {"request": self.request}


class DocumentPresignUploadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Frontend buradan presigned upload URL alır.
        Dosya backend'e gelmez.
        """
        doc_type = request.data.get("type")

        if not all([doc_type]):
            return Response(
                {"detail": "type zorunludur."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # bu kontrolü hem burada, hem de dosya finalize ederken yapıyoruz
        count = Document.objects.filter(user=request.user, type=doc_type, is_current=True).count()
        if count >= 3 and doc_type != DocumentType.PROFILE_PHOTO:
            return Response(
                {"detail": f"Aynı tipte ({doc_type}) en fazla 3 dosya yükleyebilirsiniz."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Belge tipi kontrolü
        valid_types = [c[0] for c in DocumentType.choices]
        if doc_type not in valid_types:
            return Response(
                {"detail": "Geçersiz belge tipi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # UID backend tarafından üretilir
        uid = uuid.uuid4()

        # file_key backend tarafından belirlenir
        role_path = "experts" if request.user.role == "expert" else "clients"
        file_key = f"{role_path}/{request.user.id}/{doc_type}/{uid}"

        presigned = storage.presign_upload(
            key=file_key
        )

        return Response({
            "uid": str(uid),
            "file_key": file_key,
            "upload": presigned
        })
        

class DocumentDeleteView(DestroyAPIView):
    lookup_field = "uid"
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(
            user=self.request.user,
            is_current=True
        )
    
    def perform_destroy(self, instance):
        # Business rules
        if instance.verified:
            raise ValidationError("Verified document cannot be deleted.")

        if instance.is_primary:
            raise ValidationError("Primary document cannot be deleted.")

        file_key = instance.file_key

        # DB state (atomic)
        with transaction.atomic():
            instance.is_current = False
            instance.is_primary = False
            instance.save(update_fields=["is_current", "is_primary"])

        # Storage delete (side-effect)
        try:
            storage.delete(file_key)
        except Exception as exc:
            logger.error(
                "Storage delete failed",
                extra={
                    "file_key": file_key,
                    "document_uid": str(instance.uid),
                    "error": str(exc)
                }
            )
