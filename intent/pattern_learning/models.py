from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UsageEvent:
    actor: str
    raw_input: str
    intent_type: str
    routing_target: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionResult:
    predicted_intent: str
    predicted_target: str
    confidence: float
    basis: list[str]


@dataclass
class AutomationProposal:
    name: str
    trigger_intent: str
    target: str
    confidence: float
    repeated_count: int
    steps: list[str]
    basis: list[str]
