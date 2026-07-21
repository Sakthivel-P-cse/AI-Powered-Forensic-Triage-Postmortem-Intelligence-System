import json

from ._base import wrap_prompt

SCHEMA = """{
  "timeline":  [{ "timestamp": "", "event": "", "significance": "" }],
  "gaps":      [{ "start": "", "end": "", "duration_min": 0, "flag_reason": "" }],
  "anomalies": [{ "description": "", "severity": "LOW|MEDIUM|HIGH" }],
  "movement_summary": "",
  "risk_flags":       [],
  "reasoning_chain":  []
}"""


def cctv_log_analysis_prompt(sorted_events: list[dict], subject_profile: dict | None = None) -> str:
    instructions = (
        "The events below are already sorted chronologically and pre-flagged "
        "for temporal gaps by a deterministic stage. Reconstruct the movement "
        "narrative and identify behavioral anomalies (loitering, re-entry, "
        "backtracking, unusual speed). Never describe individuals beyond what "
        "the logs state. The 'gaps' field must be copied verbatim from the "
        "deterministic stage — do not invent gaps the input does not contain."
    )
    payload = json.dumps(
        {
            "subject_profile": subject_profile or {},
            "sorted_events": sorted_events,
        },
        ensure_ascii=False,
        indent=2,
    )
    return wrap_prompt(instructions=instructions, schema_json=SCHEMA, payload=payload)
