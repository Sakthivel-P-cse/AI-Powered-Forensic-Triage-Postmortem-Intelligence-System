from datetime import datetime
from typing import Any
from pydantic import BaseModel


class EvidenceOut(BaseModel):
    id: str
    case_id: str
    file_type: str
    storage_url: str
    bytes_uploaded: int
    ocr_text_excerpt: str | None = None
    autopsy_analysis: dict[str, Any] | None = None
    upload_by: str
    created_at: datetime
