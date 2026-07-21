"""Append-only audit log.

Production: writes a row into Supabase `audit_logs`. Skeleton: in-memory
ring buffer with a JSONL fallback to ./audit.log for grep-ability.
"""
from __future__ import annotations

import json
import logging
import threading
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from db.supabase_client import supabase

log = logging.getLogger(__name__)

_AUDIT_FILE = Path("./audit.log")
_RING_MAX = 5000


@dataclass
class AuditLog:
    user_id: str
    action: str
    entity_type: str
    entity_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class _AuditSink:
    def __init__(self) -> None:
        self._ring: deque[AuditLog] = deque(maxlen=_RING_MAX)
        self._lock = threading.Lock()

    def write(self, entry: AuditLog) -> None:
        with self._lock:
            self._ring.append(entry)
            try:
                with _AUDIT_FILE.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
            except OSError as e:
                log.warning("audit file write failed: %s", e)

            sb = supabase()
            if sb is not None:
                try:
                    sb.table("audit_logs").insert(asdict(entry)).execute()
                except Exception as e:
                    log.warning("audit supabase write failed: %s", e)

    def recent(self, n: int = 100) -> list[AuditLog]:
        with self._lock:
            return list(self._ring)[-n:]


_SINK = _AuditSink()


def audit(
    *,
    user_id: str,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    _SINK.write(
        AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata or {},
        )
    )


def recent(n: int = 100) -> list[AuditLog]:
    return _SINK.recent(n)
