from __future__ import annotations

from collections import Counter

from intent.pattern_learning.models import PredictionResult


class UsagePatternPredictor:
    def predict(self, events: list[dict]) -> PredictionResult:
        if not events:
            return PredictionResult(
                predicted_intent="unknown",
                predicted_target="intent.router",
                confidence=0.0,
                basis=["no usage history"],
            )

        recent = events[-12:]
        intent_counter = Counter(event["intent_type"] for event in recent)
        target_counter = Counter(event["routing_target"] for event in recent)
        predicted_intent, intent_count = intent_counter.most_common(1)[0]
        predicted_target, _ = target_counter.most_common(1)[0]

        confidence = round(intent_count / len(recent), 4)
        basis = [
            f"recent event window: {len(recent)}",
            f"dominant intent: {predicted_intent}",
            f"dominant target: {predicted_target}",
        ]
        return PredictionResult(
            predicted_intent=predicted_intent,
            predicted_target=predicted_target,
            confidence=confidence,
            basis=basis,
        )
