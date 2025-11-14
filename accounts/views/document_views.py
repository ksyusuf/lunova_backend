# accounts/views/document_views.py
from accounts.serializers.document_serializers import DocumentSerializer
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from accounts.models import Document
from django.http import FileResponse, JsonResponse
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

        # UID kontrolü
        try:
            uid_obj = uuid.UUID(uid)
        except ValueError:
            return JsonResponse({"detail": "Geçersiz UID formatı."}, status=400)

        # DB'de kayıt var mı?
        try:
            document = Document.objects.get(
                uid=uid_obj,
                type=doc_type,
                user=request.user,
                file__icontains=filename
            )
        except Document.DoesNotExist:
            return JsonResponse({"detail": "Belge kaydı bulunamadı."}, status=404)

        # FİZİKSEL DOSYA GERÇEKTEN VAR MI?
        try:
            file_handle = document.file.open('rb')
        except FileNotFoundError:
            return JsonResponse({
                "detail": "Dosya sunucuda bulunamadı.",
                "error": "file_missing"
            }, status=404)
        except Exception:
            return JsonResponse({
                "detail": "Dosya okunurken bir hata oluştu."
            }, status=500)

        # Her şey yolundaysa dosyayı gönder
        return FileResponse(file_handle, filename=filename)
