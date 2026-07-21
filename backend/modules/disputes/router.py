"""Per-finding dispute API.

Investigators or analysts can flag any AI-generated finding as DISPUTED.
Disputes don't delete the finding — they attach a reviewable record that
travels with the case and is audit-logged. ANALYST sign-off can later
acknowledge or override them.
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
# (case_id, finding_id) → row
_MEM: dict[tuple[str, str], dict[str, Any]] = {}

DISPUTE_ROLES = (Role.INVESTIGATOR, Role.ANALYST, Role.ADMIN)


class DisputeCreate(BaseModel):
    case_id: str
    finding_id: str = Field(..., description="Stable id for the finding (e.g. 'cause_of_death', 'c1')")
    reason: str
    module: str | None = None


class DisputeOut(BaseModel):
    id: str
    case_id: str
    finding_id: str
    reason: str
    module: str | None
    raised_by: str
    raised_at: datetime


def _put(row: dict[str, Any]) -> None:
    sb = supabase()
    if sb is not None:
        sb.table("dispute_flags").insert(row).execute()
        return
    with _LOCK:
        _MEM[(row["case_id"], row["finding_id"])] = row


def _list(case_id: str) -> list[dict[str, Any]]:
    sb = supabase()
    if sb is not None:
        res = sb.table("dispute_flags").select("*").eq("case_id", case_id).execute()
        return res.data or []
    with _LOCK:
        return [v for k, v in _MEM.items() if k[0] == case_id]


@router.post("", response_model=DisputeOut, status_code=status.HTTP_201_CREATED)
async def raise_dispute(
    body: DisputeCreate,
    user: CurrentUser = Depends(require_roles(*DISPUTE_ROLES)),
) -> DisputeOut:
    if cases_repo.get_case(body.case_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "case not found")
    row = {
        "id": str(uuid.uuid4()),
        "case_id": body.case_id,
        "finding_id": body.finding_id,
        "reason": body.reason.strip(),
        "module": body.module,
        "raised_by": user.sub,
        "raised_at": datetime.now(timezone.utc),
    }
    if not row["reason"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "reason required")
    _put(row)
    audit(
        user_id=user.sub,
        action="dispute.raise",
        entity_type="case",
        entity_id=body.case_id,
        metadata={"finding_id": body.finding_id, "module": body.module},
    )
    return DisputeOut(**row)


@router.get("/{case_id}", response_model=list[DisputeOut])
async def list_for_case(
    case_id: str,
    _: CurrentUser = Depends(require_roles(*DISPUTE_ROLES)),
) -> list[DisputeOut]:
    if cases_repo.get_case(case_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "case not found")
    return [DisputeOut(**r) for r in _list(case_id)]
