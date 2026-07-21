from dataclasses import asdict

from fastapi import APIRouter, Depends

from audit import audit
from auth.rbac import CurrentUser, Role, require_roles

from .analyzer import CallRecord, GPSPing, detect_call_flags
from .schemas import CallAnalyzeRequest, CallAnalyzeResponse, CallFlagOut

router = APIRouter()


@router.post("/analyze", response_model=CallAnalyzeResponse)
async def analyze(
    body: CallAnalyzeRequest,
    user: CurrentUser = Depends(require_roles(Role.INVESTIGATOR, Role.ANALYST, Role.ADMIN)),
) -> CallAnalyzeResponse:
    calls = [CallRecord(**c.model_dump()) for c in body.calls]
    gps = [GPSPing(**g.model_dump()) for g in body.gps_context]
    flags = detect_call_flags(calls, gps)

    counts = {
        "tower_gps_mismatch": sum(1 for f in flags if f.kind == "tower_gps_mismatch"),
        "active_call_during_movement": sum(
            1 for f in flags if f.kind == "active_call_during_movement"
        ),
    }
    audit(
        user_id=user.sub,
        action="call.analyze",
        entity_type="case",
        entity_id=None,
        metadata={"calls": len(calls), **counts},
    )
    return CallAnalyzeResponse(
        flags=[CallFlagOut(**asdict(f)) for f in flags],
        counts=counts,
    )
