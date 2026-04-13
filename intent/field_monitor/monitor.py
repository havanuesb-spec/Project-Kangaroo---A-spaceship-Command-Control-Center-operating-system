from __future__ import annotations

from dataclasses import asdict
from typing import Any

from intent.field_monitor.analyzer import IntentFieldAnalyzer
from intent.field_monitor.memory import IntentFieldMemory
from trust.trust_registry import TrustRegistry


class IntentFieldMonitor:
    def __init__(
        self,
        analyzer: IntentFieldAnalyzer | None = None,
        memory: IntentFieldMemory | None = None,
        trust_registry: TrustRegistry | None = None,
    ) -> None:
        self.analyzer = analyzer or IntentFieldAnalyzer()
        self.memory = memory or IntentFieldMemory()
        self.trust_registry = trust_registry or TrustRegistry()

    def update(
        self,
        events: list[dict],
        prediction: dict | None = None,
        automation: dict | None = None,
    ) -> dict[str, Any]:
        state = self.analyzer.analyze(events=events, prediction=prediction, automation=automation)
        payload = {
            "state": asdict(state),
            "event_count": len(events),
            "prediction": prediction,
            "automation": automation,
        }
        self.memory.write_snapshot(state)
        self.memory.append_timeline(payload)
        record = self.trust_registry.issue_record(
            record_type="intent-field-monitor",
            source="IntentFieldMonitor",
            payload=payload,
        )
        payload["trust_record_hash"] = record.integrity_hash
        return payload
