import json

from ._base import wrap_prompt

SCHEMA = """{
  "cause_of_death":   { "value": "", "confidence": 0.0 },
  "manner_of_death":  { "value": "", "confidence": 0.0 },
  "injuries":         [{ "description": "", "location": "", "severity": "Mild|Moderate|Severe" }],
  "toxicology":       [{ "substance": "", "level": "", "significance": "" }],
  "weapon_indicators": [],
  "postmortem_indicators": {
    "rigor_mortis":  "",
    "livor_mortis":  "",
    "body_temp_celsius": null
  },
  "key_observations":   [],
  "conflicts_in_report": [],
  "summary":             "",
  "overall_confidence":  0.0,
  "reasoning_chain":     []
}"""


def forensic_autopsy_prompt(autopsy_text: str, case_context: dict | None = None) -> str:
    instructions = (
        "Extract structured findings from the autopsy text below. Do not infer "
        "beyond what is explicitly stated. If a field is not present, leave it "
        "as null/empty. Confidence must be assigned per field, not for the "
        "whole report. The 'conflicts_in_report' field MUST list any internal "
        "inconsistencies you observe in the source text."
    )
    payload = json.dumps(
        {"case_context": case_context or {}, "autopsy_text": autopsy_text},
        ensure_ascii=False,
        indent=2,
    )
    return wrap_prompt(instructions=instructions, schema_json=SCHEMA, payload=payload)
