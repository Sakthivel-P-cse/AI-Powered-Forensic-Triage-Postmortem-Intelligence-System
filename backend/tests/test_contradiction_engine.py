from datetime import datetime, timedelta, timezone

from modules.correlation.contradiction_engine import Event, detect_contradictions


def _ts(minute_offset: float) -> datetime:
    return datetime(2026, 5, 8, 2, 0, tzinfo=timezone.utc) + timedelta(minutes=minute_offset)


def test_impossible_travel_flag():
    """11.4 km in 6.3 min — even at 100 km/h needs 6.84 min → IMPOSSIBLE."""
    events = [
        Event(source="GPS", subject_id="S1", timestamp=_ts(0), lat=13.1010, lon=80.1620),
        Event(source="CCTV", subject_id="S1", timestamp=_ts(6.3), lat=13.0488, lon=80.2521),
    ]
    out = detect_contradictions(events)
    assert len(out) == 1
    c = out[0]
    assert c.type == "IMPOSSIBLE"
    assert 11.2 <= c.distance_km <= 11.5
    assert abs(c.time_delta_min - 6.3) < 0.05


def test_suspicious_within_band():
    """Distance reachable but only within 1.5× of minimum — SUSPICIOUS."""
    # 9.5 km in 6.3 min: drive_highway needs ~5.7 min < 6.3 < 5.7*1.5 = 8.55 → SUSPICIOUS.
    events = [
        Event(source="GPS", subject_id="S1", timestamp=_ts(0), lat=13.0902, lon=80.1751),
        Event(source="CCTV", subject_id="S1", timestamp=_ts(6.3), lat=13.0488, lon=80.2521),
    ]
    out = detect_contradictions(events)
    assert any(c.type == "SUSPICIOUS" for c in out)


def test_same_source_pairs_ignored():
    events = [
        Event(source="GPS", subject_id="S1", timestamp=_ts(0), lat=13.0, lon=80.0),
        Event(source="GPS", subject_id="S1", timestamp=_ts(1), lat=14.0, lon=81.0),
    ]
    assert detect_contradictions(events) == []


def test_different_subject_pairs_ignored():
    events = [
        Event(source="GPS", subject_id="A", timestamp=_ts(0), lat=13.0, lon=80.0),
        Event(source="CCTV", subject_id="B", timestamp=_ts(1), lat=14.0, lon=81.0),
    ]
    assert detect_contradictions(events) == []


def test_unverifiable_when_geo_missing():
    events = [
        Event(source="CCTV", subject_id="S1", timestamp=_ts(0), location_label="CAM-04"),
        Event(source="GPS", subject_id="S1", timestamp=_ts(5), location_label="CAM-12"),
    ]
    out = detect_contradictions(events)
    assert len(out) == 1
    assert out[0].type == "UNVERIFIABLE"
    assert out[0].distance_km == 0.0
