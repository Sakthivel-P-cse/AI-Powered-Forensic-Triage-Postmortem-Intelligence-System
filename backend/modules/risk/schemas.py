from typing import Any, Literal
from pydantic import BaseModel, Field


class RiskRequest(BaseModel):
    longest_cctv_gap_min: float = 0.0
    impossible_contradictions: int = 0
    suspicious_contradictions: int = 0
    unverifiable_contradictions: int = 0
    cell_tower_gps_mismatch: bool = False
    missing_gps_in_key_window: bool = False
    tod_contradicts_alibi: bool = False
    partial_autopsy_conflict: bool = False
    re_entry_pattern: bool = False
    loitering_at_scene: bool = False
    unusual_movement_speed: bool = False
    case_summary: dict[str, Any] = Field(default_factory=dict)


class FactorOut(BaseModel):
    name: str
    value: int
    max: int
    note: str


class RiskResponse(BaseModel):
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    factor_breakdown: list[FactorOut]
    investigation_briefing: str = ""
    recommended_next_steps: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    ai_cached: bool = False
