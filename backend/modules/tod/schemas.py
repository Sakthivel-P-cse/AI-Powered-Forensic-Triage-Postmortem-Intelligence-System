from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class TODRequest(BaseModel):
    body_temp_c: Optional[float] = None
    ambient_temp_c: Optional[float] = None
    body_weight_kg: Optional[float] = None
    clothing: Optional[Literal["none", "light", "heavy"]] = None
    rigor: Optional[Literal["absent", "onset", "full", "partial_resolution", "complete_resolution"]] = None
    livor: Optional[Literal["absent", "blanchable", "fixed_onset", "fixed"]] = None
    scene_conditions: dict[str, Any] = Field(default_factory=dict)


class TODResponse(BaseModel):
    indicator_window_hours: list[float]
    corrected_window_hours: list[float]
    confidence: Literal["LOW", "MEDIUM", "HIGH"]
    reasoning: str
    caveats: list[str]
    ai_cached: bool = False
