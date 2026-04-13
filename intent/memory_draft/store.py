from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from intent.memory_draft.models import MemoryDraftEntry


MEMORY_DRAFT_ROOT = Path(__file__).resolve().parent
DATA_DIR = MEMORY_DRAFT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ENTRIES_FILE = DATA_DIR / "entries.jsonl"


class MemoryDraftStore:
    def append(self, entry: MemoryDraftEntry) -> None:
        with ENTRIES_FILE.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(entry), sort_keys=True) + "\n")

    def load(self) -> list[dict]:
        if not ENTRIES_FILE.exists():
            return []
        rows: list[dict] = []
        for line in ENTRIES_FILE.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows
