"""Per-case ingestion endpoints.

POST  /api/cases/{case_id}/cctv      bulk-ingest CCTV log events
GET   /api/cases/{case_id}/cctv      list ingested events
POST  /api/cases/{case_id}/gps       bulk-ingest GPS pings
GET   /api/cases/{case_id}/gps
POST  /api/cases/{case_id}/calls     bulk-ingest call records
GET   /api/cases/{case_id}/calls

Bulk routes accept an array; persisted via the generic repos so the rest
of the system reads them out of the same place.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from audit import audit
from auth.rbac import CurrentUser, Role, require_roles
from db.repos import call_repo, cctv_repo, gps_repo
from modules.cases import repo as cases_repo

router = APIRouter()

INGESTOR_ROLES = (Role.INVESTIGATOR, Role.ANALYST, Role.ADMIN)


class CCTVEventIn(BaseModel):
    camera_id: str
    location: str
    event_timestamp: datetime
    event_type: str
    attributes: dict[str, Any] = {}


class GPSPingIn(BaseModel):
    subject_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    accuracy_m: float | None = None
    source: str | None = None


class CallRecordIn(BaseModel):
    subject_id: str
    timestamp: datetime
    duration_sec: int
    cell_tower_id: str | None = None
    call_type: str


def _require_case(case_id: str) -> None:
    if cases_repo.get_case(case_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "case not found")


# ------------- CCTV -------------
@router.post("/{case_id}/cctv", status_code=status.HTTP_201_CREATED)
async def ingest_cctv(
    case_id: str,
    rows: list[CCTVEventIn],
    user: CurrentUser = Depends(require_roles(*INGESTOR_ROLES)),
):
    _require_case(case_id)
    n = cctv_repo.insert_many(case_id, [r.model_dump(mode="json") for r in rows])
    audit(user_id=user.sub, action="ingest.cctv", entity_type="case", entity_id=case_id,
          metadata={"rows": n})
    return {"inserted": n}


@router.get("/{case_id}/cctv")
async def list_cctv(case_id: str, _: CurrentUser = Depends(require_roles(*INGESTOR_ROLES))):
    _require_case(case_id)
    return cctv_repo.list_for_case(case_id)


# ------------- GPS -------------
@router.post("/{case_id}/gps", status_code=status.HTTP_201_CREATED)
async def ingest_gps(
    case_id: str,
    rows: list[GPSPingIn],
    user: CurrentUser = Depends(require_roles(*INGESTOR_ROLES)),
):
    _require_case(case_id)
    n = gps_repo.insert_many(case_id, [r.model_dump(mode="json") for r in rows])
    audit(user_id=user.sub, action="ingest.gps", entity_type="case", entity_id=case_id,
          metadata={"rows": n})
    return {"inserted": n}


@router.get("/{case_id}/gps")
async def list_gps(case_id: str, _: CurrentUser = Depends(require_roles(*INGESTOR_ROLES))):
    _require_case(case_id)
    return gps_repo.list_for_case(case_id)


# ------------- Calls -------------
@router.post("/{case_id}/calls", status_code=status.HTTP_201_CREATED)
async def ingest_calls(
    case_id: str,
    rows: list[CallRecordIn],
    user: CurrentUser = Depends(require_roles(*INGESTOR_ROLES)),
):
    _require_case(case_id)
    n = call_repo.insert_many(case_id, [r.model_dump(mode="json") for r in rows])
    audit(user_id=user.sub, action="ingest.call", entity_type="case", entity_id=case_id,
          metadata={"rows": n})
    return {"inserted": n}


@router.get("/{case_id}/calls")
async def list_calls(case_id: str, _: CurrentUser = Depends(require_roles(*INGESTOR_ROLES))):
    _require_case(case_id)
    return call_repo.list_for_case(case_id)
