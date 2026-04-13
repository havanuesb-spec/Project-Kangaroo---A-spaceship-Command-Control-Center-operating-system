from __future__ import annotations

from dataclasses import asdict
from typing import Any

from intent.memory_draft.models import MemoryDraftEntry
from intent.memory_draft.store import MemoryDraftStore
from intent.memory_draft.summary import MemoryDraftSummarizer
from trust.trust_registry import TrustRegistry


class MemoryDraftEngine:
    def __init__(
        self,
        store: MemoryDraftStore | None = None,
        summarizer: MemoryDraftSummarizer | None = None,
        trust_registry: TrustRegistry | None = None,
    ) -> None:
        self.store = store or MemoryDraftStore()
        self.summarizer = summarizer or MemoryDraftSummarizer()
        self.trust_registry = trust_registry or TrustRegistry()

    def record(
        self,
        key: str,
        content: str,
        tags: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        entry = MemoryDraftEntry(
            key=key,
            content=content,
            tags=tags or [],
            context=context or {},
        )
        self.store.append(entry)
        entries = self.store.load()
        summary = self.summarizer.summarize(entries)
        payload = {
            "entry": asdict(entry),
            "summary": asdict(summary),
        }
        record = self.trust_registry.issue_record(
            record_type="memory-draft",
            source="MemoryDraftEngine",
            payload=payload,
        )
        payload["trust_record_hash"] = record.integrity_hash
        return payload
