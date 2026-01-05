from abc import ABC, abstractmethod


class StorageProvider(ABC):

    @abstractmethod
    def presign_upload(self, key: str, content_type: str, expires: int = 300) -> dict:
        """
        Upload için presigned URL üretir.
        Dönüş:
        {
            "url": "...",
            "method": "PUT",
            "headers": {...}
        }
        """
        pass

    @abstractmethod
    def presign_download(self, key: str, expires: int = 600) -> str:
        """Download için presigned URL üretir"""
        pass

    @abstractmethod
    def delete(self, key: str):
        """Storage'dan dosya siler"""
        pass
