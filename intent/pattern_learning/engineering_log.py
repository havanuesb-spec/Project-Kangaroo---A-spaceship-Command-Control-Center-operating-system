from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PATTERN_ROOT = Path(__file__).resolve().parent
LOG_DIR = PATTERN_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
INTENT_LOG = LOG_DIR / "calculated_intent_log.jsonl"


class EngineeringIntentLog:
    def append(self, payload: dict[str, Any]) -> None:
        line = json.dumps(payload, sort_keys=True)
        with INTENT_LOG.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
