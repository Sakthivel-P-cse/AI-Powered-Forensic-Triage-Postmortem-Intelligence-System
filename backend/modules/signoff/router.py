"""Forensic Analyst sign-off gate.

A signed report unlocks export. Signatures are immutable: re-signing the
same case is a no-op (returns the original record). Disputed findings can
be attached at sign-off time and are stored alongside the signature.
"""
from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from audit import audit
from auth.rbac import CurrentUser, Role, require_roles
from db.supabase_client import supabase
from modules.cases import repo as cases_repo

router = APIRouter()

_LOCK = threading.Lock()
_MEM: dict[str, dict[str, Any]] = {}


class SignOffRequest(BaseModel):
    disputed_findings: list[str] = Field(default_factory=list)


class SignOffOut(BaseModel):
    id: str
    case_id: str
    analyst_id: str
    signed_at: datetime
    disputed_findings: list[str]


def _get(case_id: str) -> dict[str, Any] | None:
    sb = supabase()
    if sb is not None:
        res = sb.table("report_signoffs").select("*").eq("case_id", case_id).limit(1).execute()
        return (res.data or [None])[0]
    with _LOCK:
        return _MEM.get(case_id)


def _put(row: dict[str, Any]) -> None:
    sb = supabase()
    if sb is not None:
        sb.table("report_signoffs").insert(row).execute()
        return
    with _LOCK:
        _MEM[row["case_id"]] = row


@router.get("/{case_id}", response_model=SignOffOut | None)
async def get_signoff(case_id: str, _: CurrentUser = Depends(require_roles(Role.INVESTIGATOR, Role.ANALYST, Role.ADMIN))):
    row = _get(case_id)
    if not row:
        return None
    return SignOffOut(**row)


@router.post("/{case_id}", response_model=SignOffOut, status_code=status.HTTP_201_CREATED)
async def create_signoff(
    case_id: str,
    body: SignOffRequest,
    user: CurrentUser = Depends(require_roles(Role.ANALYST, Role.ADMIN)),
) -> SignOffOut:
    if cases_repo.get_case(case_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "case not found")

    existing = _get(case_id)
    if existing:
        # Immutable — return existing rather than overwrite.
        audit(
            user_id=user.sub,
            action="signoff.attempt_duplicate",
            entity_type="case",
            entity_id=case_id,
        )
        return SignOffOut(**existing)

    row = {
        "id": str(uuid.uuid4()),
        "case_id": case_id,
        "analyst_id": user.sub,
        "signed_at": datetime.now(timezone.utc),
        "disputed_findings": body.disputed_findings,
    }
    _put(row)
    cases_repo.update_case(case_id, {"status": "REVIEW", "analyst_id": user.sub})

    audit(
        user_id=user.sub,
        action="signoff.create",
        entity_type="case",
        entity_id=case_id,
        metadata={"disputed_count": len(body.disputed_findings)},
    )
    return SignOffOut(**row)
