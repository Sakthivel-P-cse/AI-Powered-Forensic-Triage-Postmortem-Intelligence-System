"""Shared FIPL prompt scaffolding.

Every FIPL prompt opens with the same role assignment, closes with the
same scope limitation, and carries the same uncertainty + chain-of-reasoning
instructions. The wrappers here keep that contract enforceable from one place.
"""
from __future__ import annotations

ROLE_PREAMBLE = (
    "You are a forensic analysis assistant supporting a certified forensic "
    "examiner. Your output will be reviewed by a qualified professional "
    "before any investigative use."
)

UNCERTAINTY_RULE = (
    "If evidence is insufficient to support a finding, state "
    "INSUFFICIENT_EVIDENCE for that field. Never fabricate. Never infer "
    "beyond what is explicitly present in the input."
)

CHAIN_RULE = (
    "For each finding, cite the specific evidence element that supports it "
    "in the reasoning_chain[]. Each entry must reference an input fragment, "
    "not generic knowledge."
)

TERMINOLOGY_RULE = (
    "Use standard forensic terminology. Avoid casual language. Do not use "
    "ambiguous phrasing such as 'might', 'could be', 'seems' — instead "
    "report a confidence score and state the supporting evidence."
)

CONTRADICTION_RULE = (
    "If two evidence elements conflict, you MUST report the conflict in "
    "conflicts_in_report[] (or equivalent field). Do not silently choose one."
)

SCOPE_LIMIT = (
    "Your analysis is investigative support only. Do not state conclusions "
    "as facts. Do not assign criminal liability. Do not name individuals "
    "beyond what is present in the input. Output only valid JSON matching "
    "the schema provided."
)


def wrap_prompt(*, instructions: str, schema_json: str, payload: str) -> str:
    """Compose a FIPL prompt from the four mandatory blocks."""
    return f"""{ROLE_PREAMBLE}

{TERMINOLOGY_RULE}

{UNCERTAINTY_RULE}

{CHAIN_RULE}

{CONTRADICTION_RULE}

TASK INSTRUCTIONS
-----------------
{instructions.strip()}

OUTPUT SCHEMA (JSON, return EXACTLY this shape; null/[] for unknowns)
--------------------------------------------------------------------
{schema_json.strip()}

INPUT PAYLOAD
-------------
{payload.strip()}

{SCOPE_LIMIT}
"""
