from __future__ import annotations

from dataclasses import asdict
from typing import Any

from intent.pattern_learning.automation_planner import AutomationPlanner
from intent.pattern_learning.engineering_log import EngineeringIntentLog
from intent.pattern_learning.memory import PatternMemory
from intent.pattern_learning.models import UsageEvent
from intent.pattern_learning.predictor import UsagePatternPredictor
from trust.trust_registry import TrustRegistry


class PatternLearningEngine:
    def __init__(
        self,
        memory: PatternMemory | None = None,
        predictor: UsagePatternPredictor | None = None,
        automation_planner: AutomationPlanner | None = None,
        engineering_log: EngineeringIntentLog | None = None,
        trust_registry: TrustRegistry | None = None,
    ) -> None:
        self.memory = memory or PatternMemory()
        self.predictor = predictor or UsagePatternPredictor()
        self.automation_planner = automation_planner or AutomationPlanner()
        self.engineering_log = engineering_log or EngineeringIntentLog()
        self.trust_registry = trust_registry or TrustRegistry()

    def observe_and_predict(
        self,
        actor: str,
        raw_input: str,
        intent_type: str,
        routing_target: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event = UsageEvent(
            actor=actor,
            raw_input=raw_input,
            intent_type=intent_type,
            routing_target=routing_target,
            context=context or {},
        )
        self.memory.append_event(event)
        events = self.memory.load_events()
        prediction = self.predictor.predict(events)
        automation = self.automation_planner.propose(events)

        summary = {
            "observed_events": len(events),
            "latest_intent": intent_type,
            "predicted_next_intent": prediction.predicted_intent,
            "predicted_next_target": prediction.predicted_target,
            "prediction_confidence": prediction.confidence,
            "automation_candidate": automation.name if automation else None,
        }
        self.memory.write_summary(summary)

        log_payload = {
            "observed_event": asdict(event),
            "prediction": asdict(prediction),
            "automation": asdict(automation) if automation else None,
            "summary": summary,
        }
        self.engineering_log.append(log_payload)

        record = self.trust_registry.issue_record(
            record_type="pattern-learning-observation",
            source="PatternLearningEngine",
            payload=log_payload,
        )
        return {
            "event": asdict(event),
            "prediction": asdict(prediction),
            "automation": asdict(automation) if automation else None,
            "summary": summary,
            "events": events,
            "trust_record_hash": record.integrity_hash,
        }
