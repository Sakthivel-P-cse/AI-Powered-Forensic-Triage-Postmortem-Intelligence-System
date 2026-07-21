"""Supabase client (skeleton).

Initialise with `create_client(url, key)` from supabase-py. The DAO layer
in modules/* uses this client to read/write the tables defined in
db/schema.sql.
"""
from __future__ import annotations

from functools import lru_cache

from config import get_settings


@lru_cache
def supabase():
    s = get_settings()
    if not (s.supabase_url and s.supabase_service_role_key):
        return None
    from supabase import create_client
    return create_client(s.supabase_url, s.supabase_service_role_key)
