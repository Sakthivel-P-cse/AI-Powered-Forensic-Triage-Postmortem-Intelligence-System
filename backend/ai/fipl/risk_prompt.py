import json

from ._base import wrap_prompt

SCHEMA = """{
  "risk_score": 0,
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "factor_breakdown": [{ "name": "", "value": 0, "max": 0, "note": "" }],
  "investigation_briefing": "",
  "recommended_next_steps": [],
  "caveats": []
}"""


def risk_explanation_prompt(score: int, factor_breakdown: list[dict], case_summary: dict) -> str:
    instructions = (
        "The risk_score and factor_breakdown below were computed by a "
        "deterministic weighted scorer. You MUST NOT change them — copy them "
        "into the output verbatim. Your task is to produce: "
        "(a) an 'investigation_briefing' in plain forensic language explaining "
        "what the scoring factors mean for the investigation; "
        "(b) a list of 'recommended_next_steps' tied to the highest-weight "
        "factors; and (c) a 'caveats' list noting where evidence is thin. "
        "Each next-step must reference a specific factor or evidence element."
    )
    payload = json.dumps(
        {
            "deterministic_score": score,
            "deterministic_factors": factor_breakdown,
            "case_summary": case_summary,
        },
        ensure_ascii=False,
        indent=2,
    )
    return wrap_prompt(instructions=instructions, schema_json=SCHEMA, payload=payload)
