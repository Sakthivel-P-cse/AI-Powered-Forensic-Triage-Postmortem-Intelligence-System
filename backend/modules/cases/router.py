from fastapi import APIRouter, Depends, HTTPException, status

from audit import audit
from auth.rbac import CurrentUser, Role, get_current_user, require_roles

from . import repo
from .schemas import CaseCreate, CaseOut, CaseUpdate, CaseDetailOut
from db.repos import ai_results_repo, gps_repo

router = APIRouter()


def _can_view(case_row: dict, user: CurrentUser) -> bool:
    """Investigators can only view cases they created. Analysts and admins
    see all cases. Spec: 'Investigators cannot access other investigators' cases'."""
    if user.role in (Role.ANALYST, Role.ADMIN):
        return True
    return case_row.get("created_by") == user.sub


@router.get("", response_model=list[CaseOut])
async def list_(user: CurrentUser = Depends(get_current_user)) -> list[CaseOut]:
    rows = repo.list_cases()
    return [CaseOut(**c) for c in rows if _can_view(c, user)]


@router.post("", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
async def create(
    body: CaseCreate,
    user: CurrentUser = Depends(require_roles(Role.INVESTIGATOR, Role.ANALYST, Role.ADMIN)),
) -> CaseOut:
    try:
        row = repo.create_case(body.model_dump(), created_by=user.sub)
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e)) from e
    audit(user_id=user.sub, action="case.create", entity_type="case", entity_id=row["id"])
    return CaseOut(**row)


def _get_latest_ai(case_id: str, module: str) -> dict | None:
    results = ai_results_repo.list_for_case(case_id)
    module_results = [r for r in results if r["module"] == module]
    if not module_results:
        return None
    latest = max(module_results, key=lambda x: x["created_at"])
    return latest["output"]


@router.get("/{case_id}", response_model=CaseDetailOut)
async def get(case_id: str, user: CurrentUser = Depends(get_current_user)) -> CaseDetailOut:
    row = repo.get_case(case_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "case not found")
    if not _can_view(row, user):
        # Same shape as not-found to avoid leaking case existence to investigators.
        raise HTTPException(status.HTTP_404_NOT_FOUND, "case not found")
    
    # Aggregate AI results
    row["autopsy"] = _get_latest_ai(case_id, "autopsy")
    row["cctv"] = _get_latest_ai(case_id, "cctv")
    row["correlation"] = _get_latest_ai(case_id, "correlation")
    row["risk"] = _get_latest_ai(case_id, "risk")
    row["gps"] = gps_repo.list_for_case(case_id)
    
    if row.get("risk"):
        row["risk"]["score"] = row["risk_score"]
        row["risk"]["level"] = row["risk_level"]
    else:
        row["risk"] = {"score": row["risk_score"], "level": row["risk_level"]}

    return CaseDetailOut(**row)


@router.patch("/{case_id}", response_model=CaseOut)
async def update(
    case_id: str,
    body: CaseUpdate,
    user: CurrentUser = Depends(require_roles(Role.ANALYST, Role.ADMIN)),
) -> CaseOut:
    patch = {k: v for k, v in body.model_dump().items() if v is not None}
    row = repo.update_case(case_id, patch)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "case not found")
    audit(
        user_id=user.sub,
        action="case.update",
        entity_type="case",
        entity_id=case_id,
        metadata={"fields": list(patch.keys())},
    )
    return CaseOut(**row)
