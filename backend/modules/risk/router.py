from dataclasses import asdict

from fastapi import APIRouter, Depends

from ai.fipl import risk_explanation_prompt
from ai.featherless_client import AIClient
from audit import audit
from auth.rbac import CurrentUser, Role, require_roles

from .schemas import FactorOut, RiskRequest, RiskResponse
from .scorer import RiskInput, score_case

router = APIRouter()


@router.post("/score", response_model=RiskResponse)
async def score(
    body: RiskRequest,
    user: CurrentUser = Depends(require_roles(Role.INVESTIGATOR, Role.ANALYST, Role.ADMIN)),
) -> RiskResponse:
    payload = body.model_dump()
    case_summary = payload.pop("case_summary", {})
    inp = RiskInput(**payload)
    total, level, factors = score_case(inp)
    factor_out = [FactorOut(**asdict(f)) for f in factors]

    briefing, next_steps, caveats, cached = "", [], [], True
    prompt = risk_explanation_prompt(
        score=total,
        factor_breakdown=[f.model_dump() for f in factor_out],
        case_summary=case_summary,
    )
    try:
        ai_out, cached = await AIClient().generate_json(prompt)
        briefing = str(ai_out.get("investigation_briefing") or "")
        ns = ai_out.get("recommended_next_steps") or []
        next_steps = [str(s) for s in ns if isinstance(s, str)]
        cav = ai_out.get("caveats") or []
        caveats = [str(s) for s in cav if isinstance(s, str)]
    except Exception:
        # Deterministic answer remains valid even when Gemini is unreachable.
        briefing = (
            "Risk score and factors are deterministic. AI briefing unavailable; "
            "review the factor_breakdown directly."
        )

    audit(
        user_id=user.sub,
        action="risk.score",
        entity_type="case",
        entity_id=None,
        metadata={"score": total, "level": level, "ai_cached": cached},
    )

    return RiskResponse(
        risk_score=total,
        risk_level=level,
        factor_breakdown=factor_out,
        investigation_briefing=briefing,
        recommended_next_steps=next_steps,
        caveats=caveats,
        ai_cached=cached,
    )
