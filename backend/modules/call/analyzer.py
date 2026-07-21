"""Call-log forensic checks (deterministic).

Turns call records into Event rows the contradiction engine already speaks,
and adds two domain-specific flags the engine doesn't:

  - cell_tower_vs_gps_mismatch: a call routed via tower X while a near-
    simultaneous GPS ping places the subject far from that tower's nominal
    coverage centre.
  - active_call_during_movement: a call active for >N seconds while CCTV/GPS
    show the subject covering distance inconsistent with stationary phone use.

These flags feed the risk scorer (`cell_tower_gps_mismatch`,
`unusual_movement_speed`) without re-implementing them there.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from modules.correlation.contradiction_engine import Event
from modules.correlation.haversine import haversine_km


@dataclass
class CallRecord:
    subject_id: str
    timestamp: datetime
    duration_sec: int
    cell_tower_id: str
    call_type: str
    tower_lat: float | None = None
    tower_lon: float | None = None


@dataclass
class GPSPing:
    subject_id: str
    timestamp: datetime
    lat: float
    lon: float


@dataclass
class CallFlag:
    kind: str  # "tower_gps_mismatch" | "active_call_during_movement"
    timestamp: datetime
    detail: str
    severity: str  # "LOW" | "MEDIUM" | "HIGH"


# Heuristic radius beyond which a tower-routed call disagrees with a GPS ping.
TOWER_RADIUS_KM = 3.0
# Window in which a GPS ping is considered "near-simultaneous" with the call start.
NEAR_SIMULTANEOUS = timedelta(minutes=5)


def calls_to_events(calls: Iterable[CallRecord]) -> list[Event]:
    """Project call records into engine Events using tower coordinates when known."""
    out: list[Event] = []
    for c in calls:
        out.append(
            Event(
                source="CALL",
                subject_id=c.subject_id,
                timestamp=c.timestamp,
                lat=c.tower_lat,
                lon=c.tower_lon,
                location_label=f"tower:{c.cell_tower_id}",
                extra={"duration_sec": c.duration_sec, "call_type": c.call_type},
            )
        )
    return out


def detect_call_flags(calls: list[CallRecord], gps: list[GPSPing]) -> list[CallFlag]:
    flags: list[CallFlag] = []
    for c in calls:
        # Find the GPS ping closest in time within the simultaneous window.
        candidates = [
            g
            for g in gps
            if g.subject_id == c.subject_id
            and abs(g.timestamp - c.timestamp) <= NEAR_SIMULTANEOUS
        ]
        if not candidates or c.tower_lat is None or c.tower_lon is None:
            continue
        nearest = min(candidates, key=lambda g: abs(g.timestamp - c.timestamp))
        d = haversine_km(c.tower_lat, c.tower_lon, nearest.lat, nearest.lon)
        if d > TOWER_RADIUS_KM:
            flags.append(
                CallFlag(
                    kind="tower_gps_mismatch",
                    timestamp=c.timestamp,
                    detail=(
                        f"call routed via {c.cell_tower_id} but GPS ping "
                        f"{d:.1f} km from tower centre at {nearest.timestamp.isoformat()}"
                    ),
                    severity="HIGH" if d > 8 else "MEDIUM",
                )
            )

    # active_call_during_movement: any call where the subject's GPS moved >1 km
    # between the call start and start+duration window.
    for c in calls:
        end = c.timestamp + timedelta(seconds=c.duration_sec)
        pings = sorted(
            (g for g in gps if g.subject_id == c.subject_id and c.timestamp <= g.timestamp <= end),
            key=lambda g: g.timestamp,
        )
        if len(pings) < 2:
            continue
        first, last = pings[0], pings[-1]
        d = haversine_km(first.lat, first.lon, last.lat, last.lon)
        if d >= 1.0 and c.duration_sec >= 30:
            flags.append(
                CallFlag(
                    kind="active_call_during_movement",
                    timestamp=c.timestamp,
                    detail=(
                        f"{c.duration_sec}s call while subject moved {d:.2f} km "
                        f"({first.timestamp.isoformat()} → {last.timestamp.isoformat()})"
                    ),
                    severity="MEDIUM",
                )
            )
    return flags
