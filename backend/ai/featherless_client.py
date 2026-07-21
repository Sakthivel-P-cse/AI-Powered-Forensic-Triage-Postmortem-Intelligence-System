"""Async AI client using Featherless AI with caching and retry.

In skeleton mode (no FEATHERLESS_API_KEY) the client returns a deterministic stub
so the rest of the system runs without live network access.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any

from config import get_settings
from .cache import get_cache, hash_input

log = logging.getLogger(__name__)


class AIClient:
    def __init__(self, model: str | None = None):
        s = get_settings()
        self.model = model or s.featherless_model
        self.api_key = s.featherless_api_key
        self.cache = get_cache()
        self._async_client = None

    def _get_async_client(self):
        if self._async_client is None and self.api_key:
            from openai import AsyncOpenAI

            self._async_client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.featherless.ai/v1",
            )
        return self._async_client

    async def _call_sdk(self, prompt: str) -> str:
        client = self._get_async_client()
        if client is None:
            raise RuntimeError("FEATHERLESS_API_KEY not configured")

        # Adding a system prompt specifically asking for JSON to improve reliability
        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a forensic analysis AI. Always output valid JSON only. Do not output markdown fences or explanatory text outside the JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    async def generate_json(
        self,
        prompt: str,
        *,
        retries: int = 2,
        backoff_seconds: float = 1.5,
        case_id: str | None = None,
        module: str | None = None,
    ) -> tuple[dict[str, Any], bool]:
        """Return (parsed_json, was_cached)."""
        key = hash_input(prompt, self.model)
        cached = self.cache.get(key)
        if cached is not None:
            return cached.output, True

        if not self.api_key:
            stub = _stub_response(prompt)
            self.cache.set(key, stub, self.model, case_id=case_id, module=module)
            return stub, False

        last_err: Exception | None = None
        for attempt in range(retries + 1):
            try:
                raw = await self._call_sdk(prompt)
                parsed = _safe_parse_json(raw)
                self.cache.set(key, parsed, self.model, case_id=case_id, module=module)
                return parsed, False
            except Exception as e:
                last_err = e
                log.warning("Featherless AI attempt %d failed: %s", attempt + 1, e)
                await asyncio.sleep(backoff_seconds * (2 ** attempt))
        raise RuntimeError(f"Featherless AI call failed after {retries + 1} attempts: {last_err}")


def _safe_parse_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        # strip ```json fences if present
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
            
    # Fix common trailing commas before } or ]
    text = re.sub(r',\s*(?=[\]}])', '', text)
    
    # Primitive truncation repair: attempt to balance braces and brackets
    open_braces = text.count('{') - text.count('}')
    open_brackets = text.count('[') - text.count(']')
    
    if open_brackets > 0 or open_braces > 0:
        text += ']' * max(0, open_brackets)
        text += '}' * max(0, open_braces)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI response was not valid JSON: {e}; got: {text[:200]}") from e


def _stub_response(prompt: str) -> dict[str, Any]:
    """Deterministic placeholder used when FEATHERLESS_API_KEY is unset.

    The shape is deliberately generic so callers can layer their own
    schema-aware fallbacks. Production code paths SHOULD never read this.
    """
    return {
        "_stub": True,
        "_note": "FEATHERLESS_API_KEY not configured; returning skeleton stub.",
        "summary": "Stub response — configure Featherless AI to receive analysis.",
        "reasoning_chain": ["stub-mode active"],
    }
