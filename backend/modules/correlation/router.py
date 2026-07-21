from dataclasses import asdict

from fastapi import APIRouter, Depends

from ai.fipl import timeline_correlation_prompt
from ai.featherless_client import AIClient
from audit import audit
from auth.rbac import CurrentUser, Role, require_roles

from .contradiction_engine import Event, detect_contradictions
from .schemas import ContradictionOut, CorrelationRequest, CorrelationResponse

router = APIRouter()

PRIORITY_FROM_TYPE = {
    "IMPOSSIBLE": "CRITICAL",
    "SUSPICIOUS": "HIGH",
    "UNVERIFIABLE": "LOW",
}


@router.post("/detect", response_model=CorrelationResponse)
async def detect(
    body: CorrelationRequest,
    user: CurrentUser = Depends(require_roles(Role.INVESTIGATOR, Role.ANALYST, Role.ADMIN)),
) -> CorrelationResponse:
    # 1) Deterministic stage — authoritative.
    events = [
        Event(
            source=e.source,
            subject_id=e.subject_id,
            timestamp=e.timestamp,
            lat=e.lat,
            lon=e.lon,
            location_label=e.location_label,
            extra=e.extra,
        )
        for e in body.events
    ]
    found = detect_contradictions(events)
    contradictions = []
    for c in found:
        d = asdict(c)
        d["investigative_priority"] = PRIORITY_FROM_TYPE[c.type]
        contradictions.append(ContradictionOut(**d))

    summary = (
        f"{sum(1 for x in found if x.type == 'IMPOSSIBLE')} impossible · "
        f"{sum(1 for x in found if x.type == 'SUSPICIOUS')} suspicious · "
        f"{sum(1 for x in found if x.type == 'UNVERIFIABLE')} unverifiable."
    )

    # 2) FIPL refinement — only narrative, never the math.
    if contradictions:
        prompt = timeline_correlation_prompt(
            contradiction_matrix=[c.model_dump(mode="json") for c in contradictions],
            unified_events=[e.model_dump(mode="json") for e in body.events],
        )
        client = AIClient()
        try:
            ai_out, cached = await client.generate_json(prompt)
        except Exception:  # network/sdk failure must not break the deterministic answer
            ai_out, cached = {}, False

        # Merge AI 'explanation' & 'investigative_priority' onto deterministic rows
        # by (source_a.timestamp, source_b.timestamp) pair. Type/distance/Δt are immutable.
        ai_rows = {(_pair_key(r.get("source_a"), r.get("source_b"))): r for r in ai_out.get("contradictions", [])}
        for c in contradictions:
            key = _pair_key(c.source_a, c.source_b)
            ai_row = ai_rows.get(key)
            if not ai_row:
                continue
            if isinstance(ai_row.get("explanation"), str) and ai_row["explanation"].strip():
                c.explanation = ai_row["explanation"]
            ai_pri = ai_row.get("investigative_priority")
            if ai_pri in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
                c.investigative_priority = ai_pri  # type: ignore[assignment]
        if isinstance(ai_out.get("inconsistency_summary"), str) and ai_out["inconsistency_summary"].strip():
            summary = ai_out["inconsistency_summary"]
    else:
        cached = True  # nothing to ask Gemini about

    audit(
        user_id=user.sub,
        action="correlation.detect",
        entity_type="case",
        entity_id=None,
        metadata={
            "events": len(body.events),
            "contradictions": len(contradictions),
            "ai_cached": cached,
        },
    )

    return CorrelationResponse(
        unified_timeline=sorted(body.events, key=lambda e: e.timestamp),
        contradictions=contradictions,
        inconsistency_summary=summary,
    )


def _pair_key(a: dict | None, b: dict | None) -> tuple[str, str]:
    if not a or not b:
        return ("", "")
    return (str(a.get("timestamp", "")), str(b.get("timestamp", "")))
