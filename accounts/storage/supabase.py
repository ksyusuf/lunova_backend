from supabase import create_client
from django.conf import settings
from .base import StorageProvider


class SupabaseStorage(StorageProvider):

    def __init__(self):
        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        self.bucket = settings.SUPABASE_BUCKET

    def presign_upload(self, key: str, content_type: str) -> dict:
        res = self.client.storage.from_(self.bucket).create_signed_upload_url(
            key,
        )

        return {
            "url": res["signedUrl"],
            "method": "PUT",
            "headers": {
                "Content-Type": content_type
            }
        }


    def presign_download(self, key: str, expires: int = 600) -> str:
        res = self.client.storage.from_(self.bucket).create_signed_url(
            key,
            expires
        )
        return res["signedUrl"]

    def delete(self, key: str):
        self.client.storage.from_(self.bucket).remove([key])
        
        # todo: bunun da kullanılabilmesi gerekiyor.
