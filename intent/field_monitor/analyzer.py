from __future__ import annotations

from collections import Counter

from intent.field_monitor.models import IntentFieldState


class IntentFieldAnalyzer:
    def analyze(self, events: list[dict], prediction: dict | None, automation: dict | None) -> IntentFieldState:
        if not events:
            return IntentFieldState(
                dominant_intent="unknown",
                dominant_target="intent.router",
                field_stability=0.0,
                drift_risk=1.0,
                automation_pressure=0.0,
                notes=["no routed events available"],
            )

        recent = events[-10:]
        intent_counter = Counter(event["intent_type"] for event in recent)
        target_counter = Counter(event["routing_target"] for event in recent)
        dominant_intent, dominant_count = intent_counter.most_common(1)[0]
        dominant_target, _ = target_counter.most_common(1)[0]

        field_stability = round(dominant_count / len(recent), 4)
        drift_risk = round(1.0 - field_stability, 4)
        automation_pressure = round((automation or {}).get("confidence", 0.0), 4)

        notes = [
            f"recent_window={len(recent)}",
            f"dominant_intent={dominant_intent}",
            f"dominant_target={dominant_target}",
        ]
        if prediction:
            notes.append(f"predicted_next={prediction.get('predicted_intent', 'unknown')}")
        if automation:
            notes.append(f"automation_candidate={automation.get('name', 'none')}")

        return IntentFieldState(
            dominant_intent=dominant_intent,
            dominant_target=dominant_target,
            field_stability=field_stability,
            drift_risk=drift_risk,
            automation_pressure=automation_pressure,
            notes=notes,
        )
