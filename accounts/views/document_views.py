# accounts/views/document_views.py
from accounts.serializers.document_serializers import DocumentSerializer
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from accounts.models import Document
from django.http import FileResponse, JsonResponse
from rest_framework.views import APIView
import uuid

from rest_framework.response import Response
from rest_framework import status
from accounts.storage import storage
from accounts.models import DocumentType
from appointments import serializers
from lunova_backend.settings import SUPABASE_BUCKET

permission_classes = [IsAuthenticated]

class DocumentListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

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
        filename = request.data.get("filename")
        content_type = request.data.get("content_type")

        if not all([doc_type, filename, content_type]):
            return Response(
                {"detail": "type, filename ve content_type zorunludur."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # bu kontrolü hem burada, hem de dosya finalize ederken yapıyoruz
        count = Document.objects.filter(user=request.user, type=doc_type).count()
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
        ext = filename.split(".")[-1]
        role_path = "experts" if request.user.role == "expert" else "clients"
        file_key = f"{role_path}/{request.user.id}/{doc_type}/{uid}.{ext}"

        presigned = storage.presign_upload(
            key=file_key,
            content_type=content_type,
        )

        return Response({
            "uid": str(uid),
            "file_key": file_key,
            "upload": presigned
        })