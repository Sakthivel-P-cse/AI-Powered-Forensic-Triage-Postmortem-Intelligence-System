"""Supabase Storage adapter.

Production:
    Uses the db.supabase_client to upload files to a Supabase storage bucket.
"""
from __future__ import annotations

import logging
from config import get_settings
from db.supabase_client import supabase

log = logging.getLogger(__name__)


async def upload_evidence(path: str, data: bytes, content_type: str) -> str:
    """Returns the storage URL for the uploaded blob."""
    client = supabase()
    bucket = get_settings().supabase_storage_bucket
    
    if client is None:
        log.warning("Supabase client not configured; returning stub storage URL.")
        return f"supabase://stub/{bucket}/{path}"

    try:
        # Upload using the Supabase Python SDK
        # Signature is usually: upload(path, file, file_options)
        client.storage.from_(bucket).upload(
            path, 
            data, 
            file_options={"content-type": content_type}
        )
        
        # Get public URL
        url = client.storage.from_(bucket).get_public_url(path)
        return url
    except Exception as e:
        log.error("Failed to upload evidence to Supabase: %s", e)
        raise RuntimeError(f"Storage error: {e}") from e
