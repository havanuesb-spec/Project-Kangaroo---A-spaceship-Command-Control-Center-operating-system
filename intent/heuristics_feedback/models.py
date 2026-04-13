from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HeuristicSignal:
    statement: str
    prior_statements: list[str] = field(default_factory=list)
    observed_behavior: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class HeuristicAssessment:
    consistency_score: float
    evidence_score: float
    distortion_risk: float
    reconstruction_confidence: float
    indicators: list[str]
    notes: list[str]
