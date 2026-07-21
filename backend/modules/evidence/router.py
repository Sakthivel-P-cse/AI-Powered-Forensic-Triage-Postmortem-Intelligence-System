"""Evidence upload pipeline.

upload → Firebase (encrypted at rest) → Vision OCR (when applicable)
       → autopsy analyzer (FIPL → Gemini) for *.pdf / *.txt / image inputs.

The OCR step is only invoked for media types that need it; plain text
is forwarded directly to the autopsy service.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import PurePosixPath

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from audit import audit
from auth.rbac import CurrentUser, Role, require_roles
from modules.autopsy.service import analyze_autopsy
from modules.cases import repo as cases_repo
from storage.supabase_storage import upload_evidence
from storage.ocr_client import extract_text

from .schemas import EvidenceOut

router = APIRouter()

_OCR_MIME_PREFIXES = ("image/", "application/pdf")
_TEXT_MIME_PREFIXES = ("text/",)


@router.post("/upload", response_model=EvidenceOut, status_code=status.HTTP_201_CREATED)
async def upload(
    case_id: str = Form(...),
    file_type: str = Form("autopsy", description="autopsy | cctv_log | gps_log | call_log | other"),
    file: UploadFile = File(...),
    user: CurrentUser = Depends(require_roles(Role.INVESTIGATOR, Role.ANALYST, Role.ADMIN)),
) -> EvidenceOut:
    if cases_repo.get_case(case_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "case not found")

    raw = await file.read()
    if not raw:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "empty upload")

    safe_name = PurePosixPath(file.filename or "blob").name
    blob_id = str(uuid.uuid4())
    storage_path = f"cases/{case_id}/{blob_id}/{safe_name}"
    storage_url = await upload_evidence(
        storage_path, raw, file.content_type or "application/octet-stream"
    )

    text: str | None = None
    autopsy_analysis = None
    if file_type == "autopsy":
        if (file.content_type or "").startswith(_TEXT_MIME_PREFIXES):
            text = raw.decode("utf-8", errors="replace")
        elif (file.content_type or "").startswith(_OCR_MIME_PREFIXES):
            text = await extract_text(raw)
        else:
            text = raw.decode("utf-8", errors="replace")  # best-effort

        if text and text.strip():
            output, _ = await analyze_autopsy(text, case_context={"case_id": case_id})
            autopsy_analysis = output

    audit(
        user_id=user.sub,
        action="evidence.upload",
        entity_type="case",
        entity_id=case_id,
        metadata={
            "file_type": file_type,
            "filename": safe_name,
            "bytes": len(raw),
            "ran_autopsy_analysis": autopsy_analysis is not None,
        },
    )

    return EvidenceOut(
        id=blob_id,
        case_id=case_id,
        file_type=file_type,
        storage_url=storage_url,
        bytes_uploaded=len(raw),
        ocr_text_excerpt=(text[:400] if text else None),
        autopsy_analysis=autopsy_analysis,
        upload_by=user.sub,
        created_at=datetime.now(timezone.utc),
    )
