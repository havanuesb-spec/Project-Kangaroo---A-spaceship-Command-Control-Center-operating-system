from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from trust.trust_registry import TrustRegistry


SECURITY_ROOT = Path(__file__).resolve().parent
STATE_DIR = SECURITY_ROOT / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
FLAG_FILE = STATE_DIR / "coherence_flag.json"

ERASABLE_ROOT = Path(r"C:\Multiverse\intent\heuristics_feedback\erasable_program")
CANONICAL_DIR = ERASABLE_ROOT / "canonical"
WORKING_DIR = ERASABLE_ROOT / "working"


class CoherenceGuard:
    def __init__(self, trust_registry: TrustRegistry | None = None) -> None:
        self.trust_registry = trust_registry or TrustRegistry()
        CANONICAL_DIR.mkdir(parents=True, exist_ok=True)
        WORKING_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_flag()

    def inspect_and_restore(self) -> dict[str, Any]:
        canonical_files = self._index_files(CANONICAL_DIR)
        working_files = self._index_files(WORKING_DIR)
        events: list[dict[str, Any]] = []

        for name, canonical_path in canonical_files.items():
            working_path = WORKING_DIR / name
            if not working_path.exists():
                shutil.copy2(canonical_path, working_path)
                events.append({"event": "restored-working-file", "file": name})
            elif self._digest(canonical_path) != self._digest(working_path):
                shutil.copy2(canonical_path, working_path)
                events.append({"event": "corrected-working-file", "file": name})

        for name, working_path in working_files.items():
            canonical_path = CANONICAL_DIR / name
            if not canonical_path.exists():
                shutil.copy2(working_path, canonical_path)
                events.append({"event": "rehydrated-canonical-file", "file": name})

        payload = {
            "events": events,
            "canonical_count": len(self._index_files(CANONICAL_DIR)),
            "working_count": len(self._index_files(WORKING_DIR)),
            "tamper_detected": any("corrected" in event["event"] or "restored" in event["event"] for event in events),
            "coherence_state": "stable" if not events else "reconstructed",
        }
        FLAG_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        record = self.trust_registry.issue_record(
            record_type="coherence-guard-scan",
            source="CoherenceGuard",
            payload=payload,
        )
        payload["trust_record_hash"] = record.integrity_hash
        return payload

    def _ensure_flag(self) -> None:
        if not FLAG_FILE.exists():
            FLAG_FILE.write_text(
                json.dumps(
                    {
                        "status": "initialized",
                        "monitored_root": str(ERASABLE_ROOT),
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

    def _index_files(self, root: Path) -> dict[str, Path]:
        return {
            str(path.relative_to(root)): path
            for path in root.rglob("*")
            if path.is_file()
        }

    def _digest(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()


# Compatibility alias while the codebase shifts to photonic/coherence language.
SecurityFlagGuard = CoherenceGuard
