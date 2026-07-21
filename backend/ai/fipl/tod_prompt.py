import json

from ._base import wrap_prompt

SCHEMA = """{
  "indicator_window_hours": [0, 0],
  "corrected_window_hours": [0, 0],
  "confidence": "LOW|MEDIUM|HIGH",
  "reasoning": "",
  "caveats": []
}"""


def tod_refinement_prompt(indicator_window: dict, scene_conditions: dict | None = None) -> str:
    instructions = (
        "An indicator-based time-of-death window has already been computed by "
        "a deterministic model from rigor mortis, livor mortis, and algor "
        "mortis indicators. You MUST NOT recalculate the raw window. Use the "
        "provided scene_conditions (ambient temperature trend, body position, "
        "moisture, insect activity, etc.) to: "
        "(a) optionally narrow OR widen 'corrected_window_hours' within "
        "physiological reason; "
        "(b) state your final 'confidence' (LOW/MEDIUM/HIGH); "
        "(c) write a short 'reasoning' citing which scene factor moved the "
        "window; and (d) list 'caveats' for missing inputs. "
        "If scene_conditions are absent, leave corrected_window_hours equal to "
        "indicator_window_hours and set confidence to LOW."
    )
    payload = json.dumps(
        {
            "deterministic_indicator_window": indicator_window,
            "scene_conditions": scene_conditions or {},
        },
        ensure_ascii=False,
        indent=2,
    )
    return wrap_prompt(instructions=instructions, schema_json=SCHEMA, payload=payload)
