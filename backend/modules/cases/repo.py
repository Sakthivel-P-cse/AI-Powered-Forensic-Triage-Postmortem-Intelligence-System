"""Cases repository.

Tries Supabase first; falls back to a thread-safe in-memory store keyed
by case id so the rest of the stack remains fully functional in skeleton
deployments. The shape mirrors the `cases` table.
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any

from db.supabase_client import supabase


_LOCK = threading.Lock()
_MEM: dict[str, dict[str, Any]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _seed_if_empty() -> None:
    if _MEM:
        return
    _MEM["CASE-2026-0117"] = {
        "id": "CASE-2026-0117",
        "title": "Riverside Apartments — Suspicious Death",
        "status": "IN_TRIAGE",
        "risk_score": 84,
        "risk_level": "CRITICAL",
        "created_by": None,
        "analyst_id": None,
        "created_at": _now(),
        "updated_at": _now(),
        "metadata": {"subject_id": "S-001"},
    }
    _MEM["CASE-2026-0118"] = {
        "id": "CASE-2026-0118",
        "title": "Marina Promenade — Found Deceased",
        "status": "INTAKE",
        "risk_score": 42,
        "risk_level": "MEDIUM",
        "created_by": None,
        "analyst_id": "analyst@forensic.local",
        "created_at": _now(),
        "updated_at": _now(),
        "metadata": {"subject_id": "S-002"},
    }


def list_cases() -> list[dict[str, Any]]:
    sb = supabase()
    if sb is not None:
        res = sb.table("cases").select("*").order("created_at", desc=True).execute()
        return res.data or []
    with _LOCK:
        _seed_if_empty()
        return sorted(_MEM.values(), key=lambda c: c["created_at"], reverse=True)


def get_case(case_id: str) -> dict[str, Any] | None:
    sb = supabase()
    if sb is not None:
        res = sb.table("cases").select("*").eq("id", case_id).limit(1).execute()
        return (res.data or [None])[0]
    with _LOCK:
        _seed_if_empty()
        return _MEM.get(case_id)


def create_case(payload: dict[str, Any], created_by: str | None) -> dict[str, Any]:
    row = {
        "id": payload["id"],
        "title": payload["title"],
        "status": payload.get("status", "INTAKE"),
        "risk_score": 0,
        "risk_level": "LOW",
        "created_by": created_by,
        "analyst_id": None,
        "created_at": _now(),
        "updated_at": _now(),
        "metadata": {},
    }
    sb = supabase()
    if sb is not None:
        sb.table("cases").insert(row).execute()
        return row
    with _LOCK:
        _seed_if_empty()
        if row["id"] in _MEM:
            raise ValueError("case_id already exists")
        _MEM[row["id"]] = row
        return row


def update_case(case_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:
    sb = supabase()
    patch = {**patch, "updated_at": _now()}
    if sb is not None:
        res = sb.table("cases").update(patch).eq("id", case_id).execute()
        return (res.data or [None])[0]
    with _LOCK:
        _seed_if_empty()
        cur = _MEM.get(case_id)
        if not cur:
            return None
        cur.update(patch)
        return cur
