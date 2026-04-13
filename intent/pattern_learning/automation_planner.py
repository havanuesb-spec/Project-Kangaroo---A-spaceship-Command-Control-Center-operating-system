from __future__ import annotations

from collections import Counter

from intent.pattern_learning.models import AutomationProposal


class AutomationPlanner:
    def propose(self, events: list[dict]) -> AutomationProposal | None:
        if len(events) < 3:
            return None

        pairs = [(event["intent_type"], event["routing_target"]) for event in events[-20:]]
        pair_counter = Counter(pairs)
        (intent_type, target), repeated_count = pair_counter.most_common(1)[0]

        if repeated_count < 3:
            return None

        window = min(20, len(events))
        confidence = round(repeated_count / window, 4)
        name = f"{intent_type}-automation"
        steps = self._build_steps(intent_type, target)
        basis = [
            f"window_size={window}",
            f"repeat_count={repeated_count}",
            f"dominant_pair={intent_type}->{target}",
        ]
        return AutomationProposal(
            name=name,
            trigger_intent=intent_type,
            target=target,
            confidence=confidence,
            repeated_count=repeated_count,
            steps=steps,
            basis=basis,
        )

    def _build_steps(self, intent_type: str, target: str) -> list[str]:
        steps = [
            f"detect repeated intent: {intent_type}",
            f"route work to: {target}",
            "capture trust and engineering logs",
        ]
        if target == "capabilities.processor":
            steps.append("generate or refresh the matching capability module")
        elif target == "capabilities.harvester":
            steps.append("handoff prepared payload to the harvester layer")
        elif target == "trust.trust_registry":
            steps.append("record a governance or verification trace")
        else:
            steps.append("request human confirmation before autonomous execution")
        return steps
