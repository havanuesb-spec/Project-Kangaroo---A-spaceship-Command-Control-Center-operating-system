from __future__ import annotations

from dataclasses import asdict
from typing import Any

from capabilities.processor import MultiverseProcessor
from intent.classifier import IntentClassifier
from intent.field_monitor.monitor import IntentFieldMonitor
from intent.intent_model import IntentSignal
from intent.pattern_learning.engine import PatternLearningEngine
from trust.trust_registry import TrustRegistry


class IntentRouter:
    def __init__(
        self,
        classifier: IntentClassifier | None = None,
        trust_registry: TrustRegistry | None = None,
        processor: MultiverseProcessor | None = None,
        pattern_learning: PatternLearningEngine | None = None,
        field_monitor: IntentFieldMonitor | None = None,
    ) -> None:
        self.classifier = classifier or IntentClassifier()
        self.trust_registry = trust_registry or TrustRegistry()
        self.processor = processor or MultiverseProcessor(trust_registry=self.trust_registry)
        self.pattern_learning = pattern_learning or PatternLearningEngine(trust_registry=self.trust_registry)
        self.field_monitor = field_monitor or IntentFieldMonitor(trust_registry=self.trust_registry)

    def route(self, raw_input: str, actor: str = "operator", context: dict[str, Any] | None = None) -> dict[str, Any]:
        signal = IntentSignal(raw_input=raw_input, actor=actor, context=context or {})
        plan = self.classifier.classify(signal)
        record = self.trust_registry.issue_record(
            record_type="intent-route",
            source="IntentRouter",
            payload={
                "signal": asdict(signal),
                "plan": asdict(plan),
            },
        )
        execution_result: dict[str, Any] | None = None
        if plan.routing_target == "capabilities.processor":
            processed = self.processor.process(raw_input)
            execution_result = asdict(processed)

        pattern_result = self.pattern_learning.observe_and_predict(
            actor=signal.actor,
            raw_input=signal.raw_input,
            intent_type=plan.intent_type,
            routing_target=plan.routing_target,
            context=signal.context,
        )
        field_result = self.field_monitor.update(
            events=pattern_result["events"],
            prediction=pattern_result["prediction"],
            automation=pattern_result["automation"],
        )

        return {
            "signal": asdict(signal),
            "plan": asdict(plan),
            "trust_record_hash": record.integrity_hash,
            "execution_result": execution_result,
            "pattern_learning": pattern_result,
            "intent_field_monitor": field_result,
        }
