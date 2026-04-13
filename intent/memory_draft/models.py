from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryDraftEntry:
    key: str
    content: str
    tags: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryDraftSummary:
    total_entries: int
    latest_key: str
    active_tags: list[str]
    notes: list[str]
