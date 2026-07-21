"""Autopsy analysis pipeline.

Steps (per spec):
    upload → Firebase
          → OCR (Vision)
          → text chunking (max ~3000 tokens / ~12k chars)
          → FIPL forensic_autopsy_prompt
          → Gemini
          → structured JSON
          → cached in Supabase

This service implements the chunking + Gemini hand-off. OCR/Firebase calls
are stubbed at the storage layer.
"""
from __future__ import annotations

from typing import Any

from ai.fipl import forensic_autopsy_prompt
from ai.featherless_client import AIClient

CHUNK_CHAR_LIMIT = 12000  # ~3000 tokens, conservative


def chunk_text(text: str, limit: int = CHUNK_CHAR_LIMIT) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    paragraphs = text.split("\n\n")
    buf: list[str] = []
    size = 0
    for p in paragraphs:
        if size + len(p) + 2 > limit and buf:
            chunks.append("\n\n".join(buf))
            buf, size = [], 0
        buf.append(p)
        size += len(p) + 2
    if buf:
        chunks.append("\n\n".join(buf))
    return chunks


async def analyze_autopsy(text: str, case_context: dict | None = None) -> tuple[dict[str, Any], bool]:
    chunks = chunk_text(text)
    client = AIClient()

    # Single-chunk path
    if len(chunks) == 1:
        prompt = forensic_autopsy_prompt(chunks[0], case_context)
        return await client.generate_json(prompt)

    # Multi-chunk path: analyze each, then ask the model to merge.
    partials: list[dict[str, Any]] = []
    any_cached = True
    for c in chunks:
        prompt = forensic_autopsy_prompt(c, case_context)
        out, was_cached = await client.generate_json(prompt)
        any_cached = any_cached and was_cached
        partials.append(out)

    merge_payload = "\n\n".join(
        f"PARTIAL_{i+1}:\n{p}" for i, p in enumerate(partials)
    )
    merge_prompt = forensic_autopsy_prompt(
        merge_payload,
        {**(case_context or {}), "_merge_mode": True},
    )
    out, merge_cached = await client.generate_json(merge_prompt)
    return out, any_cached and merge_cached
