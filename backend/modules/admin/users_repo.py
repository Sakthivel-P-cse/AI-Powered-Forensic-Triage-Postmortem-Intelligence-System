"""User store. Source of truth for the auth router.

The auth router pre-seeds three demo accounts on first import; this module
exposes a read/write façade that ADMIN routes use to manage them. In skeleton
mode the store is in-memory and shared with auth.router via the same dict.
"""
from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from auth.jwt_handler import hash_password
from auth.rbac import Role


_LOCK = threading.Lock()
_USERS: dict[str, dict[str, Any]] = {}


def _seed_if_empty() -> None:
    if _USERS:
        return
    seeds = [
        ("investigator@forensic.local", "demo", Role.INVESTIGATOR, "D. Iyer"),
        ("analyst@forensic.local", "demo", Role.ANALYST, "M. Krishnan"),
        ("admin@forensic.local", "demo", Role.ADMIN, "System Admin"),
    ]
    for email, pw, role, name in seeds:
        _USERS[email] = {
            "id": str(uuid.uuid4()),
            "email": email,
            "password_hash": hash_password(pw),
            "role": role,
            "name": name,
            "disabled": False,
            "created_at": datetime.now(timezone.utc),
        }


def get(email: str) -> dict[str, Any] | None:
    with _LOCK:
        _seed_if_empty()
        return _USERS.get(email.lower())


def list_all() -> list[dict[str, Any]]:
    with _LOCK:
        _seed_if_empty()
        return [{**u, "password_hash": "<redacted>"} for u in _USERS.values()]


def create(email: str, password: str, role: Role, name: str) -> dict[str, Any]:
    with _LOCK:
        _seed_if_empty()
        email = email.lower()
        if email in _USERS:
            raise ValueError("user exists")
        row = {
            "id": str(uuid.uuid4()),
            "email": email,
            "password_hash": hash_password(password),
            "role": role,
            "name": name,
            "disabled": False,
            "created_at": datetime.now(timezone.utc),
        }
        _USERS[email] = row
        return {**row, "password_hash": "<redacted>"}


def set_disabled(email: str, disabled: bool) -> dict[str, Any] | None:
    with _LOCK:
        _seed_if_empty()
        u = _USERS.get(email.lower())
        if not u:
            return None
        u["disabled"] = disabled
        return {**u, "password_hash": "<redacted>"}
