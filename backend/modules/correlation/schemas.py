from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class EventIn(BaseModel):
    source: str = Field(..., examples=["GPS", "CCTV", "CALL"])
    subject_id: str
    timestamp: datetime
    lat: Optional[float] = None
    lon: Optional[float] = None
    location_label: Optional[str] = None
    extra: dict = Field(default_factory=dict)


class ContradictionOut(BaseModel):
    type: Literal["IMPOSSIBLE", "SUSPICIOUS", "UNVERIFIABLE"]
    source_a: dict
    source_b: dict
    time_delta_min: float
    distance_km: float
    fastest_mode: Optional[str] = None
    min_travel_min: Optional[float] = None
    explanation: str
    investigative_priority: Optional[Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]] = None


class CorrelationRequest(BaseModel):
    events: list[EventIn]


class CorrelationResponse(BaseModel):
    unified_timeline: list[EventIn]
    contradictions: list[ContradictionOut]
    inconsistency_summary: str
