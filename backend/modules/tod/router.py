from fastapi import APIRouter, Depends

from ai.fipl import tod_refinement_prompt
from ai.featherless_client import AIClient
from audit import audit
from auth.rbac import CurrentUser, Role, require_roles

from .indicator_model import IndicatorInput, estimate_window
from .schemas import TODRequest, TODResponse

router = APIRouter()

_VALID_CONF = {"LOW", "MEDIUM", "HIGH"}


@router.post("/estimate", response_model=TODResponse)
async def estimate(
    body: TODRequest,
    user: CurrentUser = Depends(require_roles(Role.INVESTIGATOR, Role.ANALYST, Role.ADMIN)),
) -> TODResponse:
    inp = IndicatorInput(
        body_temp_c=body.body_temp_c,
        ambient_temp_c=body.ambient_temp_c,
        body_weight_kg=body.body_weight_kg,
        clothing=body.clothing,
        rigor=body.rigor,
        livor=body.livor,
    )
    w = estimate_window(inp)

    n_indicators = sum(1 for x in (body.body_temp_c, body.rigor, body.livor) if x is not None)
    confidence = "LOW" if n_indicators <= 1 else "MEDIUM" if n_indicators == 2 else "HIGH"
    indicator_window = list(w.indicator_window_hours)
    corrected_window = list(w.corrected_window_hours)
    reasoning = (
        f"Indicator window {w.indicator_window_hours[0]}–{w.indicator_window_hours[1]}h "
        f"derived from: {', '.join(w.contributing) or 'no inputs'}."
    )
    caveats = list(w.notes)
    cached = True

    if body.scene_conditions:
        prompt = tod_refinement_prompt(
            indicator_window={
                "indicator_window_hours": indicator_window,
                "corrected_window_hours": corrected_window,
                "contributing": w.contributing,
            },
            scene_conditions=body.scene_conditions,
        )
        try:
            ai_out, cached = await AIClient().generate_json(prompt)
        except Exception:
            ai_out = {}

        # Only the corrected window, confidence, reasoning, caveats can move.
        ai_corr = ai_out.get("corrected_window_hours")
        if (
            isinstance(ai_corr, list)
            and len(ai_corr) == 2
            and all(isinstance(v, (int, float)) for v in ai_corr)
        ):
            lo, hi = float(ai_corr[0]), float(ai_corr[1])
            if 0 <= lo <= hi <= 96:  # plausibility guard
                corrected_window = [round(lo, 1), round(hi, 1)]

        ai_conf = ai_out.get("confidence")
        if ai_conf in _VALID_CONF:
            confidence = ai_conf

        ai_reasoning = ai_out.get("reasoning")
        if isinstance(ai_reasoning, str) and ai_reasoning.strip():
            reasoning = ai_reasoning

        ai_cav = ai_out.get("caveats")
        if isinstance(ai_cav, list):
            caveats = caveats + [str(c) for c in ai_cav if isinstance(c, str)]

    audit(
        user_id=user.sub,
        action="tod.estimate",
        entity_type="case",
        entity_id=None,
        metadata={"window": corrected_window, "confidence": confidence, "ai_cached": cached},
    )

    return TODResponse(
        indicator_window_hours=indicator_window,
        corrected_window_hours=corrected_window,
        confidence=confidence,
        reasoning=reasoning,
        caveats=caveats,
        ai_cached=cached,
    )
