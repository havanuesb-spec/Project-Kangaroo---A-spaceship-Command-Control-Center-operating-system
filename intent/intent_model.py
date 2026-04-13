from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntentSignal:
    raw_input: str
    actor: str = "operator"
    domain: str = "general"
    urgency: str = "normal"
    tags: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentPlan:
    intent_type: str
    confidence: float
    actions: list[str]
    constraints: list[str]
    routing_target: str
