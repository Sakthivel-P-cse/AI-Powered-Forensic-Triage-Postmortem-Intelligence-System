from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class CallRecordIn(BaseModel):
    subject_id: str
    timestamp: datetime
    duration_sec: int
    cell_tower_id: str
    call_type: Literal["incoming", "outgoing", "missed"]
    tower_lat: float | None = None
    tower_lon: float | None = None


class GPSPingIn(BaseModel):
    subject_id: str
    timestamp: datetime
    lat: float
    lon: float


class CallAnalyzeRequest(BaseModel):
    calls: list[CallRecordIn]
    gps_context: list[GPSPingIn] = []


class CallFlagOut(BaseModel):
    kind: str
    timestamp: datetime
    detail: str
    severity: Literal["LOW", "MEDIUM", "HIGH"]


class CallAnalyzeResponse(BaseModel):
    flags: list[CallFlagOut]
    counts: dict[str, int]
