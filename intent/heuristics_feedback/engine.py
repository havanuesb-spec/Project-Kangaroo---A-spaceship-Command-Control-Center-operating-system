from __future__ import annotations

from dataclasses import asdict
from typing import Any

from intent.heuristics_feedback.memory import FeedbackMemory
from intent.heuristics_feedback.models import HeuristicSignal
from intent.heuristics_feedback.coherence_heuristics import CoherenceHeuristics
from trust.trust_registry import TrustRegistry


class HeuristicsFeedbackEngine:
    def __init__(
        self,
        heuristics: CoherenceHeuristics | None = None,
        memory: FeedbackMemory | None = None,
        trust_registry: TrustRegistry | None = None,
    ) -> None:
        self.heuristics = heuristics or CoherenceHeuristics()
        self.memory = memory or FeedbackMemory()
        self.trust_registry = trust_registry or TrustRegistry()

    def evaluate(
        self,
        statement: str,
        prior_statements: list[str] | None = None,
        observed_behavior: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        signal = HeuristicSignal(
            statement=statement,
            prior_statements=prior_statements or [],
            observed_behavior=observed_behavior or {},
            context=context or {},
        )
        assessment = self.heuristics.assess(signal)
        memory_path = self.memory.write_event("latest_feedback", signal, assessment)
        trust_record = self.trust_registry.issue_record(
            record_type="coherence-feedback",
            source="HeuristicsFeedbackEngine",
            payload={
                "signal": asdict(signal),
                "assessment": asdict(assessment),
                "memory_path": str(memory_path),
            },
        )
        return {
            "signal": asdict(signal),
            "assessment": asdict(assessment),
            "memory_path": str(memory_path),
            "trust_record_hash": trust_record.integrity_hash,
        }
