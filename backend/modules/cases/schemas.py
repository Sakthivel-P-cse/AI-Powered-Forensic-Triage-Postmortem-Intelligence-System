from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


CaseStatus = Literal["INTAKE", "IN_TRIAGE", "REVIEW", "CLOSED"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class CaseCreate(BaseModel):
    id: str = Field(..., examples=["CASE-2026-0117"])
    title: str
    status: CaseStatus = "INTAKE"


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[CaseStatus] = None
    analyst_id: Optional[str] = None
    risk_score: Optional[int] = None
    risk_level: Optional[RiskLevel] = None


class CaseOut(BaseModel):
    id: str
    title: str
    status: CaseStatus
    risk_score: int = 0
    risk_level: RiskLevel = "LOW"
    created_by: Optional[str] = None
    analyst_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)

class CaseDetailOut(CaseOut):
    autopsy: Optional[dict[str, Any]] = None
    cctv: Optional[dict[str, Any]] = None
    gps: Optional[list[dict[str, Any]]] = None
    correlation: Optional[dict[str, Any]] = None
    risk: Optional[dict[str, Any]] = None
