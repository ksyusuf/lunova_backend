# accounts/views/document_views.py
from accounts.serializers.document_serializers import DocumentSerializer
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from accounts.models import Document, DocumentType
from django.http import FileResponse, Http404, JsonResponse
from rest_framework.views import APIView
import uuid

permission_classes = [IsAuthenticated]

class DocumentListView(ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)
    
    
class DocumentUploadView(CreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class DocumentRetrieveView(APIView):
    """
    Kullanıcıya ait belgeyi UID, type ve filename ile döndürür.
    """
    permission_classes = [IsAuthenticated]


    def get(self, request, *args, **kwargs):
        doc_type = request.query_params.get("type")
        uid = request.query_params.get("uid")
        filename = request.query_params.get("filename")

        if not all([doc_type, uid, filename]):
            return JsonResponse({"detail": "Eksik parametre."}, status=400)

        # UID geçerli bir UUID mi kontrol et
        try:
            uid_obj = uuid.UUID(uid)
        except ValueError:
            return JsonResponse({"detail": "Geçersiz UID formatı."}, status=400)

        try:
            document = Document.objects.get(
                uid=uid_obj,
                type=doc_type,
                user=request.user,
                file__icontains=filename
            )
        except Document.DoesNotExist:
            raise Http404("Belge bulunamadı.")

        # Dosya yanıtı
        response = FileResponse(document.file.open('rb'), filename=filename)
        return response