from __future__ import annotations

from collections import Counter

from intent.memory_draft.models import MemoryDraftSummary


class MemoryDraftSummarizer:
    def summarize(self, entries: list[dict]) -> MemoryDraftSummary:
        if not entries:
            return MemoryDraftSummary(
                total_entries=0,
                latest_key="none",
                active_tags=[],
                notes=["no memory drafts recorded"],
            )

        tag_counter = Counter(tag for entry in entries for tag in entry.get("tags", []))
        active_tags = [tag for tag, _ in tag_counter.most_common(5)]
        latest_key = entries[-1]["key"]
        return MemoryDraftSummary(
            total_entries=len(entries),
            latest_key=latest_key,
            active_tags=active_tags,
            notes=[f"latest_key={latest_key}", f"active_tag_count={len(active_tags)}"],
        )
