"""Deterministic risk scoring (0..100).

Weights per spec:
    timeline_gaps              ≤ 20
    contradiction_severity     ≤ 25
    gps_call_inconsistency     ≤ 20
    autopsy_scene_inconsistency ≤ 20
    behavioral_anomalies       ≤ 15
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


@dataclass
class Factor:
    name: str
    value: int
    max: int
    note: str


@dataclass
class RiskInput:
    longest_cctv_gap_min: float = 0.0
    impossible_contradictions: int = 0
    suspicious_contradictions: int = 0
    unverifiable_contradictions: int = 0
    cell_tower_gps_mismatch: bool = False
    missing_gps_in_key_window: bool = False
    tod_contradicts_alibi: bool = False
    partial_autopsy_conflict: bool = False
    re_entry_pattern: bool = False
    loitering_at_scene: bool = False
    unusual_movement_speed: bool = False


def _gap_points(min_: float) -> tuple[int, str]:
    if min_ < 5:
        return 0, "no significant CCTV gap"
    if min_ < 15:
        return 5, f"{min_:.1f}-min gap (5–15)"
    if min_ < 60:
        return 12, f"{min_:.1f}-min gap (15–60)"
    return 20, f"{min_:.1f}-min gap (>60)"


def _contradiction_points(imp: int, sus: int, unv: int) -> tuple[int, str]:
    score = 0
    parts: list[str] = []
    if imp > 0:
        score += 25
        parts.append(f"{imp} IMPOSSIBLE")
    elif sus > 0:
        score += 15
        parts.append(f"{sus} SUSPICIOUS")
    if unv > 0:
        score += min(15, 5 * unv)
        parts.append(f"{unv} UNVERIFIABLE")
    score = min(25, score)
    return score, ", ".join(parts) or "no contradictions"


def _gps_call_points(tower_mismatch: bool, missing: bool) -> tuple[int, str]:
    score = (10 if tower_mismatch else 0) + (10 if missing else 0)
    notes = []
    if tower_mismatch:
        notes.append("cell-tower vs GPS mismatch")
    if missing:
        notes.append("missing GPS in key window")
    return min(20, score), ", ".join(notes) or "GPS/call consistent"


def _autopsy_points(contradicts: bool, partial: bool) -> tuple[int, str]:
    if contradicts:
        return 20, "TOD contradicts subject alibi"
    if partial:
        return 10, "partial autopsy/scene conflict"
    return 0, "no autopsy/scene conflict"


def _behavior_points(reentry: bool, loiter: bool, speed: bool) -> tuple[int, str]:
    score = (5 if reentry else 0) + (7 if loiter else 0) + (3 if speed else 0)
    notes = []
    if reentry: notes.append("re-entry pattern")
    if loiter: notes.append("loitering")
    if speed: notes.append("unusual movement speed")
    return min(15, score), ", ".join(notes) or "no behavioral flags"


def level_for_score(score: int) -> RiskLevel:
    if score >= 81:
        return "CRITICAL"
    if score >= 61:
        return "HIGH"
    if score >= 31:
        return "MEDIUM"
    return "LOW"


def score_case(inp: RiskInput) -> tuple[int, RiskLevel, list[Factor]]:
    g_v, g_n = _gap_points(inp.longest_cctv_gap_min)
    c_v, c_n = _contradiction_points(
        inp.impossible_contradictions,
        inp.suspicious_contradictions,
        inp.unverifiable_contradictions,
    )
    p_v, p_n = _gps_call_points(inp.cell_tower_gps_mismatch, inp.missing_gps_in_key_window)
    a_v, a_n = _autopsy_points(inp.tod_contradicts_alibi, inp.partial_autopsy_conflict)
    b_v, b_n = _behavior_points(inp.re_entry_pattern, inp.loitering_at_scene, inp.unusual_movement_speed)

    factors = [
        Factor("Timeline gaps (CCTV)", g_v, 20, g_n),
        Factor("Contradiction severity", c_v, 25, c_n),
        Factor("GPS / call inconsistency", p_v, 20, p_n),
        Factor("Autopsy / scene inconsistency", a_v, 20, a_n),
        Factor("Behavioral anomalies", b_v, 15, b_n),
    ]
    total = sum(f.value for f in factors)
    return total, level_for_score(total), factors
