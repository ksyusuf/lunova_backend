from django.conf import settings
from .base import StorageProvider
from urllib.parse import quote


class MockStorage(StorageProvider):
    """
    Local / test ortamı için SupabaseStorage mock'u.
    Gerçek dosya işlemi yapmaz, sadece davranışı simüle eder.
    """

    def __init__(self):
        self.base_url = getattr(
            settings,
            "MOCK_STORAGE_BASE_URL",
            "http://localhost:8000/mock-storage"
        )

    def presign_upload(self, key: str, content_type: str) -> dict:
        """
        Supabase create_signed_upload_url taklidi
        """
        safe_key = quote(key)

        return {
            "url": f"{self.base_url}/upload/{safe_key}",
            "method": "PUT",
            "headers": {
                "Content-Type": content_type
            }
        }

    def presign_download(self, key: str, expires: int = 600) -> str:
        """
        Supabase create_signed_url taklidi
        """
        safe_key = quote(key)
        return f"{self.base_url}/download/{safe_key}?expires={expires}"

    def delete(self, key: str):
        """
        Gerçekte hiçbir şey silmez.
        DB kaydı silindiğinde 'silinmiş varsayılır'.
        """
        return None
