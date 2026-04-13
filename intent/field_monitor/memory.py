from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from intent.field_monitor.models import IntentFieldState


FIELD_ROOT = Path(__file__).resolve().parent
STATE_DIR = FIELD_ROOT / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
SNAPSHOT_FILE = STATE_DIR / "intent_field_snapshot.json"
TIMELINE_FILE = STATE_DIR / "intent_field_timeline.jsonl"


class IntentFieldMemory:
    def write_snapshot(self, state: IntentFieldState) -> None:
        SNAPSHOT_FILE.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")

    def append_timeline(self, payload: dict[str, Any]) -> None:
        with TIMELINE_FILE.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
