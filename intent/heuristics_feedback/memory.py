from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from intent.heuristics_feedback.models import HeuristicAssessment, HeuristicSignal


HEURISTICS_ROOT = Path(__file__).resolve().parent
MEMORY_DIR = HEURISTICS_ROOT / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


class FeedbackMemory:
    def __init__(self, root: Path = MEMORY_DIR) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write_event(self, event_name: str, signal: HeuristicSignal, assessment: HeuristicAssessment) -> Path:
        payload: dict[str, Any] = {
            "event_name": event_name,
            "signal": asdict(signal),
            "assessment": asdict(assessment),
        }
        filename = f"{event_name}.json"
        target = self.root / filename
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return target
