from datetime import datetime
from typing import Any
from pydantic import BaseModel


class CCTVEventIn(BaseModel):
    camera_id: str
    location: str
    timestamp: datetime
    event_type: str
    attributes: dict[str, Any] = {}


class CCTVAnalyzeRequest(BaseModel):
    events: list[CCTVEventIn]
    subject_profile: dict[str, Any] = {}


class GapOut(BaseModel):
    start: datetime
    end: datetime
    duration_min: float
    flag_reason: str


class CCTVAnalyzeResponse(BaseModel):
    sorted_events: list[CCTVEventIn]
    gaps: list[GapOut]
    cached: bool
    ai_output: dict[str, Any]
