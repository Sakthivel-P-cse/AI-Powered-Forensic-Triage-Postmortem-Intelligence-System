"""CCTV log analysis: deterministic pre-processing → FIPL → Gemini."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from ai.fipl import cctv_log_analysis_prompt
from ai.featherless_client import AIClient
from config import get_settings


# When the sorted log is longer than this, we collapse runs of same-camera
# same-event entries into '<event> ×N (start..end)' summaries before sending
# to Gemini. This is the 'token optimization summarization pass' from spec.
LARGE_LOG_THRESHOLD = 200


def detect_gaps(events: list[dict[str, Any]], threshold_min: float | None = None) -> list[dict[str, Any]]:
    threshold = threshold_min if threshold_min is not None else get_settings().cctv_gap_threshold_min
    if not events:
        return []
    sorted_e = sorted(events, key=lambda e: _parse(e["timestamp"]))
    gaps: list[dict[str, Any]] = []
    for prev, curr in zip(sorted_e, sorted_e[1:]):
        delta_min = (_parse(curr["timestamp"]) - _parse(prev["timestamp"])).total_seconds() / 60.0
        if delta_min >= threshold:
            gaps.append(
                {
                    "start": prev["timestamp"],
                    "end": curr["timestamp"],
                    "duration_min": round(delta_min, 2),
                    "flag_reason": (
                        "Camera offline" if prev.get("event_type") == "camera_offline"
                        else f"Coverage gap ≥ {threshold:.0f} min"
                    ),
                }
            )
    return gaps


def summarize_runs(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse contiguous runs of same (camera_id, event_type) into one entry.

    Saves tokens for very long deployments. Original timestamps preserved as
    'window' so the model still sees the temporal extent.
    """
    if not events:
        return []
    out: list[dict[str, Any]] = []
    run_start = events[0]
    count = 1
    for cur in events[1:]:
        same = (
            cur.get("camera_id") == run_start.get("camera_id")
            and cur.get("event_type") == run_start.get("event_type")
        )
        if same:
            count += 1
            run_end = cur
            continue
        out.append(_emit_run(run_start, run_end if count > 1 else run_start, count))
        run_start = cur
        count = 1
    out.append(_emit_run(run_start, cur if count > 1 else run_start, count))  # type: ignore[name-defined]
    return out


def _emit_run(start: dict[str, Any], end: dict[str, Any], count: int) -> dict[str, Any]:
    if count == 1:
        return start
    return {
        **start,
        "event_type": f"{start['event_type']} ×{count}",
        "window": {"start": str(start["timestamp"]), "end": str(end["timestamp"])},
    }


def _parse(ts) -> datetime:
    if isinstance(ts, datetime):
        return ts
    return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))


async def analyze_cctv(
    events: list[dict[str, Any]],
    subject_profile: dict | None = None,
    *,
    case_id: str | None = None,
) -> dict[str, Any]:
    sorted_e = sorted(events, key=lambda e: _parse(e["timestamp"]))
    gaps = detect_gaps(sorted_e)

    # Strip metadata: Keep only essential fields for the FIPL prompt
    essential_keys = {"camera_id", "location", "timestamp", "event_type", "attributes"}
    payload_events = [
        {k: v for k, v in e.items() if k in essential_keys}
        for e in sorted_e
    ]

    if len(payload_events) > LARGE_LOG_THRESHOLD:
        payload_events = summarize_runs(payload_events)

    prompt = cctv_log_analysis_prompt(
        sorted_events=[{**e, "timestamp": str(e["timestamp"])} for e in payload_events],
        subject_profile=subject_profile,
    )
    client = AIClient()
    ai_out, cached = await client.generate_json(prompt, case_id=case_id, module="cctv")
    return {
        "sorted_events": sorted_e,
        "gaps": gaps,
        "cached": cached,
        "ai_output": ai_out,
    }
