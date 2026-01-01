# storage/factory.py
from django.conf import settings
from .supabase import SupabaseStorage
from .mock import MockStorage

def get_storage():
    match settings.STORAGE_PROVIDER:
        case "supabase":
            return SupabaseStorage()
        case "mock":
            return MockStorage()
        case _:
            raise RuntimeError("Invalid STORAGE_PROVIDER")
