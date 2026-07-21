from fastapi import APIRouter, Depends

from audit import audit
from auth.rbac import CurrentUser, Role, require_roles

from .schemas import CCTVAnalyzeRequest, CCTVAnalyzeResponse
from .service import analyze_cctv

router = APIRouter()


@router.post("/analyze", response_model=CCTVAnalyzeResponse)
async def analyze(
    body: CCTVAnalyzeRequest,
    user: CurrentUser = Depends(require_roles(Role.INVESTIGATOR, Role.ANALYST, Role.ADMIN)),
) -> CCTVAnalyzeResponse:
    events = [e.model_dump() for e in body.events]
    result = await analyze_cctv(events, body.subject_profile)
    audit(
        user_id=user.sub,
        action="cctv.analyze",
        entity_type="case",
        entity_id=None,
        metadata={
            "events": len(events),
            "gaps": len(result["gaps"]),
            "ai_cached": result["cached"],
        },
    )
    return CCTVAnalyzeResponse(**result)
