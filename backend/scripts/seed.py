"""Seed the in-memory (or Supabase) repos with sample_data/* contents."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if not (ROOT / "backend").exists():
    # Docker mode
    sys.path.insert(0, "/app")
    SAMPLE = Path("/app/sample_data")
else:
    sys.path.insert(0, str(ROOT / "backend"))
    SAMPLE = ROOT / "sample_data"

from db.repos import call_repo, cctv_repo, gps_repo  # noqa: E402
from modules.cases import repo as cases_repo  # noqa: E402

DEMO_CASE_ID = "CR-2024-00471"


def _ensure_case() -> None:
    if cases_repo.get_case(DEMO_CASE_ID) is None:
        cases_repo.create_case(
            {
                "id": DEMO_CASE_ID,
                "title": "Flat 4B Block B — Suspicious Death",
                "status": "IN_TRIAGE",
            },
            created_by="seed",
        )


def _seed_cctv() -> int:
    raw = json.loads((SAMPLE / "cctv_logs.json").read_text())
    rows = []
    for r in raw:
        rows.append(
            {
                "camera_id": r["camera_id"],
                "location": r["location"],
                "event_timestamp": r["timestamp"],
                "event_type": r["event_type"],
                "attributes": r.get("attributes", {}),
            }
        )
    return cctv_repo.insert_many(DEMO_CASE_ID, rows)


def _seed_gps() -> int:
    raw = json.loads((SAMPLE / "gps_logs.json").read_text())
    return gps_repo.insert_many(DEMO_CASE_ID, [
        {
            "subject_id": r["subject_id"],
            "timestamp": r["timestamp"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "accuracy_m": r.get("accuracy_m"),
            "source": r.get("source"),
        } for r in raw
    ])


def _seed_calls() -> int:
    raw = json.loads((SAMPLE / "call_logs.json").read_text())
    return call_repo.insert_many(DEMO_CASE_ID, raw)


def main() -> None:
    _ensure_case()
    cctv_n = _seed_cctv()
    gps_n = _seed_gps()
    calls_n = _seed_calls()
    print(f"[seed] case={DEMO_CASE_ID} cctv={cctv_n} gps={gps_n} calls={calls_n}")
    print(f"[seed] {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
