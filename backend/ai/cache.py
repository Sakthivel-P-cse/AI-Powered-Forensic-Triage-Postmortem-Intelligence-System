"""Hash-based response cache for AI calls.

Production: persist (input_hash, output_json, model_version, created_at) to
the `ai_results` table in Supabase. Skeleton: in-memory only.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any


def datetime_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_input(prompt: str, model: str) -> str:
    h = hashlib.sha256()
    h.update(model.encode())
    h.update(b"\x00")
    h.update(prompt.encode())
    return h.hexdigest()


@dataclass
class CacheEntry:
    output: Any
    model: str
    created_at: float


class AICache:
    def __init__(self, ttl_days: int = 30):
        self.ttl_seconds = ttl_days * 86400
        self._store: dict[str, CacheEntry] = {}
        self._lock = Lock()

    def get(self, key: str) -> CacheEntry | None:
        with self._lock:
            e = self._store.get(key)
            if not e:
                return None
            if time.time() - e.created_at > self.ttl_seconds:
                self._store.pop(key, None)
                return None
            return e

    def set(self, key: str, output: Any, model: str, *, case_id: str | None = None,
            module: str | None = None) -> None:
        with self._lock:
            self._store[key] = CacheEntry(
                output=output, model=model, created_at=time.time()
            )
        # Best-effort persist to ai_results so cross-process workers share cache.
        try:
            from db.repos import ai_results_repo  # local import: avoids cycle at module load
            ai_results_repo.insert_many(
                case_id or "_global",
                [{
                    "module": module or "unknown",
                    "input_hash": key,
                    "output": output,
                    "model_version": model,
                    "cached": False,
                    "created_at": datetime_now_iso(),
                }],
            )
        except Exception:
            pass

    @staticmethod
    def serialize_output(out: Any) -> str:
        return json.dumps(out, sort_keys=True, ensure_ascii=False)


_default_cache: AICache | None = None


def get_cache() -> AICache:
    global _default_cache
    if _default_cache is None:
        from config import get_settings
        _default_cache = AICache(ttl_days=get_settings().ai_cache_ttl_days)
    return _default_cache
