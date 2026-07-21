import json

from ._base import wrap_prompt

SCHEMA = """{
  "unified_timeline": [],
  "contradictions":   [{
    "type": "IMPOSSIBLE|SUSPICIOUS|UNVERIFIABLE",
    "source_a": {},
    "source_b": {},
    "time_delta_min": 0,
    "distance_km": 0,
    "explanation": "",
    "investigative_priority": "LOW|MEDIUM|HIGH|CRITICAL"
  }],
  "evidence_links":      [],
  "inconsistency_summary": ""
}"""


def timeline_correlation_prompt(contradiction_matrix: list[dict], unified_events: list[dict]) -> str:
    instructions = (
        "The contradiction matrix below was produced by a deterministic engine "
        "using Haversine distance and minimum-travel-time logic. Do NOT alter "
        "type, time_delta_min, or distance_km — those are mathematical facts. "
        "Your job is to: (a) write a plain-language 'explanation' for each "
        "contradiction in forensic terminology; and (b) assign an "
        "'investigative_priority' (LOW/MEDIUM/HIGH/CRITICAL) based on the "
        "type and the proximity of events to the unified timeline. "
        "Then produce a short 'inconsistency_summary' for the case as a whole."
    )
    payload = json.dumps(
        {
            "deterministic_contradictions": contradiction_matrix,
            "unified_timeline": unified_events,
        },
        ensure_ascii=False,
        indent=2,
    )
    return wrap_prompt(instructions=instructions, schema_json=SCHEMA, payload=payload)
