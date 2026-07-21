from fastapi import APIRouter, Depends

from audit import audit
from auth.rbac import CurrentUser, Role, require_roles

from .schemas import AutopsyAnalyzeRequest, AutopsyAnalyzeResponse
from .service import analyze_autopsy

router = APIRouter()


@router.post("/analyze", response_model=AutopsyAnalyzeResponse)
async def analyze(
    body: AutopsyAnalyzeRequest,
    user: CurrentUser = Depends(require_roles(Role.INVESTIGATOR, Role.ANALYST, Role.ADMIN)),
) -> AutopsyAnalyzeResponse:
    output, cached = await analyze_autopsy(body.text, body.case_context)
    audit(
        user_id=user.sub,
        action="autopsy.analyze",
        entity_type="case",
        entity_id=body.case_context.get("case_id") if body.case_context else None,
        metadata={"chars": len(body.text), "ai_cached": cached},
    )
    return AutopsyAnalyzeResponse(cached=cached, output=output)
