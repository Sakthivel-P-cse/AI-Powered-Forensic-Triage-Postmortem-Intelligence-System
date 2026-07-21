"""Cross-source temporal contradiction engine (deterministic).

Pairs every event from a different source belonging to the same subject and
flags pairs that are mathematically inconsistent given minimum travel time.

Severity ladder per spec:
    - IMPOSSIBLE   : delta_t < min_travel_time
    - SUSPICIOUS   : min_travel_time <= delta_t < min_travel_time * SUSPICIOUS_MULTIPLIER
    - UNVERIFIABLE : pair has no usable spatial reference
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, Literal

from config import get_settings
from .haversine import haversine_km

Severity = Literal["IMPOSSIBLE", "SUSPICIOUS", "UNVERIFIABLE"]
TransportMode = Literal["walking", "driving_urban", "driving_highway", "transit"]


@dataclass
class Event:
    """A timestamped event from any source."""
    source: str                       # "GPS" | "CCTV" | "CALL" | ...
    subject_id: str
    timestamp: datetime
    lat: float | None = None
    lon: float | None = None
    location_label: str | None = None
    extra: dict = field(default_factory=dict)


@dataclass
class Contradiction:
    type: Severity
    source_a: dict
    source_b: dict
    time_delta_min: float
    distance_km: float
    fastest_mode: TransportMode | None
    min_travel_min: float | None
    explanation: str


def _speed_kmh(mode: TransportMode) -> float:
    s = get_settings()
    return {
        "walking": s.walk_kmh,
        "driving_urban": s.drive_urban_kmh,
        "driving_highway": s.drive_highway_kmh,
        "transit": s.transit_kmh,
    }[mode]


def _fastest_mode(distance_km: float) -> tuple[TransportMode, float]:
    """Pick the mode with the shortest travel time for the given distance."""
    candidates: list[TransportMode] = ["driving_highway", "driving_urban", "transit", "walking"]
    best: tuple[TransportMode, float] | None = None
    for mode in candidates:
        t_min = (distance_km / _speed_kmh(mode)) * 60.0
        if best is None or t_min < best[1]:
            best = (mode, t_min)
    return best  # type: ignore[return-value]


def _ev_to_dict(e: Event) -> dict:
    return {
        "source": e.source,
        "subject_id": e.subject_id,
        "timestamp": e.timestamp.isoformat(),
        "lat": e.lat,
        "lon": e.lon,
        "location_label": e.location_label,
    }


def detect_contradictions(events: Iterable[Event]) -> list[Contradiction]:
    """Compare every cross-source pair of events for the same subject.

    Pairs from the *same* source are not contradictions — they form trajectories,
    not cross-corroboration.
    """
    s = get_settings()
    evs = sorted(events, key=lambda e: e.timestamp)
    out: list[Contradiction] = []

    for i, a in enumerate(evs):
        for b in evs[i + 1 :]:
            if a.subject_id != b.subject_id:
                continue
            if a.source == b.source:
                continue

            dt_min = (b.timestamp - a.timestamp).total_seconds() / 60.0
            if dt_min < 0:
                continue  # safety, but list is sorted

            has_geo = (
                a.lat is not None and a.lon is not None
                and b.lat is not None and b.lon is not None
            )

            if not has_geo:
                # Without coordinates we cannot verify; flag once if locations differ.
                if a.location_label and b.location_label and a.location_label != b.location_label:
                    out.append(
                        Contradiction(
                            type="UNVERIFIABLE",
                            source_a=_ev_to_dict(a),
                            source_b=_ev_to_dict(b),
                            time_delta_min=round(dt_min, 2),
                            distance_km=0.0,
                            fastest_mode=None,
                            min_travel_min=None,
                            explanation=(
                                f"Movement between '{a.location_label}' and "
                                f"'{b.location_label}' cannot be verified without "
                                "configured inter-location distance."
                            ),
                        )
                    )
                continue

            dist_km = haversine_km(a.lat, a.lon, b.lat, b.lon)
            mode, min_t = _fastest_mode(dist_km)

            if dt_min + 1e-6 < min_t:
                severity: Severity = "IMPOSSIBLE"
                explain = (
                    f"Events {dist_km:.2f} km apart but only "
                    f"{dt_min:.1f} min elapsed. Fastest plausible mode "
                    f"({mode}) requires ≥{min_t:.1f} min."
                )
            elif dt_min < min_t * s.suspicious_multiplier:
                severity = "SUSPICIOUS"
                explain = (
                    f"{dist_km:.2f} km in {dt_min:.1f} min implies "
                    f"{dist_km / (dt_min / 60.0):.0f} km/h — within 1.5× of "
                    f"the minimum travel time for {mode}; review."
                )
            else:
                continue

            out.append(
                Contradiction(
                    type=severity,
                    source_a=_ev_to_dict(a),
                    source_b=_ev_to_dict(b),
                    time_delta_min=round(dt_min, 2),
                    distance_km=round(dist_km, 3),
                    fastest_mode=mode,
                    min_travel_min=round(min_t, 2),
                    explanation=explain,
                )
            )

    return out
