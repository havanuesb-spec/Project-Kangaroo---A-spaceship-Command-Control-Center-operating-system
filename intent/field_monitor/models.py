from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IntentFieldState:
    dominant_intent: str
    dominant_target: str
    field_stability: float
    drift_risk: float
    automation_pressure: float
    notes: list[str]
