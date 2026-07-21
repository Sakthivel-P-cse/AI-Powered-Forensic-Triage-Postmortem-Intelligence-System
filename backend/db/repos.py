"""Generic per-table repos with Supabase + in-memory fallback.

Every repo follows the same shape:
    list_for_case(case_id) -> list[dict]
    insert_many(case_id, rows) -> int (count)
    delete_for_case(case_id) -> int

Used by ingestion endpoints, the contradiction pipeline, and the seed
script so business logic never reaches into supabase directly.
"""
from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Iterable

from db.supabase_client import supabase


_LOCK = threading.Lock()
_MEM: dict[str, dict[str, list[dict[str, Any]]]] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bucket(table: str) -> dict[str, list[dict[str, Any]]]:
    with _LOCK:
        return _MEM.setdefault(table, {})


class _Repo:
    def __init__(self, table: str):
        self.table = table

    def list_for_case(self, case_id: str) -> list[dict[str, Any]]:
        sb = supabase()
        if sb is not None:
            res = sb.table(self.table).select("*").eq("case_id", case_id).execute()
            return res.data or []
        return list(_bucket(self.table).get(case_id, []))

    def insert_many(self, case_id: str, rows: Iterable[dict[str, Any]]) -> int:
        prepared: list[dict[str, Any]] = []
        for r in rows:
            row = {**r}
            row.setdefault("id", str(uuid.uuid4()))
            row["case_id"] = case_id
            prepared.append(row)
        if not prepared:
            return 0
        sb = supabase()
        if sb is not None:
            sb.table(self.table).insert(prepared).execute()
            return len(prepared)
        with _LOCK:
            _MEM.setdefault(self.table, {}).setdefault(case_id, []).extend(prepared)
            return len(prepared)

    def delete_for_case(self, case_id: str) -> int:
        sb = supabase()
        if sb is not None:
            res = sb.table(self.table).delete().eq("case_id", case_id).execute()
            return len(res.data or [])
        with _LOCK:
            existing = _MEM.get(self.table, {}).pop(case_id, [])
            return len(existing)


cctv_repo = _Repo("cctv_logs")
gps_repo = _Repo("gps_logs")
call_repo = _Repo("call_logs")
contradictions_repo = _Repo("contradictions")
autopsy_repo = _Repo("autopsy_reports")
ai_results_repo = _Repo("ai_results")
