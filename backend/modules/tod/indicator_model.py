"""Deterministic postmortem-indicator → time-of-death window.

The Gemini layer never computes the raw window. It only refines an estimate
produced here, given environmental/scene context.

Indicator tables (from spec):

  Algor mortis (cooling):
      TOD_hours ≈ (37 - body_temp_°C) / 0.83
      modifiers: ambient temp, weight, clothing

  Rigor mortis stage → window (h since death):
      Absent              → 0–2
      Onset (jaw/neck)    → 2–6
      Full                → 6–12
      Partial resolution  → 12–24
      Complete resolution → 24–48

  Livor mortis stage → window (h):
      Absent                       → 0–2
      Blanchable                   → 2–8
      Fixed onset                  → 8–12
      Fixed (non-blanchable)       → 12–48
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


RigorStage = Literal["absent", "onset", "full", "partial_resolution", "complete_resolution"]
LivorStage = Literal["absent", "blanchable", "fixed_onset", "fixed"]


RIGOR_TABLE: dict[RigorStage, tuple[float, float]] = {
    "absent": (0.0, 2.0),
    "onset": (2.0, 6.0),
    "full": (6.0, 12.0),
    "partial_resolution": (12.0, 24.0),
    "complete_resolution": (24.0, 48.0),
}

LIVOR_TABLE: dict[LivorStage, tuple[float, float]] = {
    "absent": (0.0, 2.0),
    "blanchable": (2.0, 8.0),
    "fixed_onset": (8.0, 12.0),
    "fixed": (12.0, 48.0),
}


@dataclass
class IndicatorInput:
    body_temp_c: Optional[float] = None
    ambient_temp_c: Optional[float] = None
    body_weight_kg: Optional[float] = None
    clothing: Optional[Literal["none", "light", "heavy"]] = None
    rigor: Optional[RigorStage] = None
    livor: Optional[LivorStage] = None


@dataclass
class IndicatorWindow:
    indicator_window_hours: tuple[float, float]
    corrected_window_hours: tuple[float, float]
    contributing: list[str]
    notes: list[str]


def _algor_window(body_temp: float, ambient: float | None, weight: float | None,
                  clothing: str | None) -> tuple[tuple[float, float], list[str]]:
    """Glaister-style cooling estimate with simple modifiers."""
    notes: list[str] = []
    base = (37.0 - body_temp) / 0.83
    if base < 0:
        base = 0.0
        notes.append("body temperature above 37 °C — cooling formula clamped to 0h")

    ambient = 21.0 if ambient is None else ambient
    # Cold environment slows cooling (window earlier); warm environment widens
    delta = (21.0 - ambient) * 0.05  # +5% per °C cooler than 21
    base *= 1.0 - max(min(delta, 0.25), -0.25)

    if weight is not None and weight < 50:
        base *= 1.10
        notes.append("low body mass — extended cooling correction +10%")
    elif weight is not None and weight > 100:
        base *= 0.92
        notes.append("high body mass — accelerated cooling correction −8%")

    if clothing == "heavy":
        base *= 0.92
        notes.append("heavy clothing — insulation correction −8%")
    elif clothing == "none":
        base *= 1.10
        notes.append("no clothing — exposure correction +10%")

    spread = max(0.5, base * 0.20)
    return (round(max(0.0, base - spread), 1), round(base + spread, 1)), notes


def _intersect(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    lo = max(a[0], b[0])
    hi = min(a[1], b[1])
    if lo > hi:
        # No intersection — fall back to the union; flag this in caller.
        return (min(a[0], b[0]), max(a[1], b[1]))
    return (lo, hi)


def estimate_window(inp: IndicatorInput) -> IndicatorWindow:
    contributing: list[str] = []
    notes: list[str] = []
    windows: list[tuple[float, float]] = []

    if inp.rigor:
        w = RIGOR_TABLE[inp.rigor]
        windows.append(w)
        contributing.append(f"rigor:{inp.rigor} → {w[0]}–{w[1]}h")
    if inp.livor:
        w = LIVOR_TABLE[inp.livor]
        windows.append(w)
        contributing.append(f"livor:{inp.livor} → {w[0]}–{w[1]}h")

    raw_window: tuple[float, float] | None = None
    if inp.body_temp_c is not None:
        algor, n = _algor_window(inp.body_temp_c, inp.ambient_temp_c, inp.body_weight_kg, inp.clothing)
        notes.extend(n)
        windows.append(algor)
        contributing.append(f"algor:Δ={37.0 - inp.body_temp_c:.1f}°C → {algor[0]}–{algor[1]}h")
        raw_window = algor

    if not windows:
        return IndicatorWindow((0.0, 48.0), (0.0, 48.0), [], ["no indicators provided"])

    indicator = windows[0]
    for w in windows[1:]:
        new = _intersect(indicator, w)
        if new[0] > new[1]:
            notes.append(f"conflicting indicators: {indicator} vs {w}; widening")
            indicator = (min(indicator[0], w[0]), max(indicator[1], w[1]))
        else:
            indicator = new

    corrected = raw_window if raw_window else indicator
    corrected = (
        max(corrected[0], indicator[0] - 1.0),
        min(corrected[1], indicator[1] + 1.0),
    )

    return IndicatorWindow(
        indicator_window_hours=(round(indicator[0], 1), round(indicator[1], 1)),
        corrected_window_hours=(round(corrected[0], 1), round(corrected[1], 1)),
        contributing=contributing,
        notes=notes,
    )
