from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from intent.pattern_learning.models import UsageEvent


PATTERN_ROOT = Path(__file__).resolve().parent
MEMORY_DIR = PATTERN_ROOT / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
EVENT_LOG = MEMORY_DIR / "usage_events.jsonl"
SUMMARY_FILE = MEMORY_DIR / "usage_summary.json"


class PatternMemory:
    def append_event(self, event: UsageEvent) -> None:
        line = json.dumps(asdict(event), sort_keys=True)
        with EVENT_LOG.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def load_events(self) -> list[dict[str, Any]]:
        if not EVENT_LOG.exists():
            return []
        events: list[dict[str, Any]] = []
        for line in EVENT_LOG.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
        return events

    def write_summary(self, payload: dict[str, Any]) -> None:
        SUMMARY_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
