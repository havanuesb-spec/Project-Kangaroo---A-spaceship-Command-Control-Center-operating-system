from __future__ import annotations

from intent.intent_model import IntentPlan, IntentSignal


class IntentClassifier:
    def classify(self, signal: IntentSignal) -> IntentPlan:
        text = signal.raw_input.lower()

        if any(word in text for word in ["solve", "equation", "matrix", "calculate", "math"]):
            return IntentPlan(
                intent_type="mathematics",
                confidence=0.92,
                actions=["identify-math-algorithm", "generate-capability", "record-trust-decision"],
                constraints=["preserve-input-trace", "require-trust-record"],
                routing_target="capabilities.processor",
            )
        if any(word in text for word in ["trust", "policy", "verify", "integrity", "audit"]):
            return IntentPlan(
                intent_type="trust-governance",
                confidence=0.89,
                actions=["evaluate-policy", "record-trust-decision"],
                constraints=["immutable-record-preferred"],
                routing_target="trust.trust_registry",
            )
        if any(word in text for word in ["run", "execute", "process", "harvest", "interject"]):
            return IntentPlan(
                intent_type="execution",
                confidence=0.84,
                actions=["prepare-execution-plan", "handoff-to-capability-layer"],
                constraints=["allowlisted-operations-only"],
                routing_target="capabilities.harvester",
            )

        return IntentPlan(
            intent_type="general-navigation",
            confidence=0.58,
            actions=["collect-context", "request-routing-decision"],
            constraints=["human-review-allowed"],
            routing_target="intent.router",
        )
