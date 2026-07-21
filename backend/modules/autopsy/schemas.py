from typing import Any
from pydantic import BaseModel


class AutopsyAnalyzeRequest(BaseModel):
    text: str
    case_context: dict[str, Any] = {}


class AutopsyAnalyzeResponse(BaseModel):
    cached: bool
    output: dict[str, Any]
