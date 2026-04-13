from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from trust.trust_registry import TrustRegistry


SECURITY_ROOT = Path(__file__).resolve().parent
BIOMETRIC_STATE = SECURITY_ROOT / "state" / "biometric_flag.json"
BIOMETRIC_STATE.parent.mkdir(parents=True, exist_ok=True)


class BiometricFlagGuard:
    def __init__(self, trust_registry: TrustRegistry | None = None) -> None:
        self.trust_registry = trust_registry or TrustRegistry()
        self.roots = {
            "iris": Path(r"C:\Multiverse\intent\iris\double_secure_iris_library_registration"),
            "voice": Path(r"C:\Multiverse\intent\voice\voice_library_registration"),
        }
        for root in self.roots.values():
            (root / "canonical").mkdir(parents=True, exist_ok=True)
            (root / "working").mkdir(parents=True, exist_ok=True)

    def inspect_and_restore(self) -> dict[str, Any]:
        domains: dict[str, Any] = {}
        tamper_detected = False
        all_events: list[dict[str, str]] = []

        for name, root in self.roots.items():
            domain_events = self._sync_pair(root / "canonical", root / "working")
            domains[name] = {"events": domain_events, "state": "stable" if not domain_events else "reconstructed"}
            all_events.extend({"domain": name, **event} for event in domain_events)
            tamper_detected = tamper_detected or bool(domain_events)

        payload = {
            "domains": domains,
            "tamper_detected": tamper_detected,
        }
        BIOMETRIC_STATE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        record = self.trust_registry.issue_record(
            record_type="biometric-guard-scan",
            source="BiometricFlagGuard",
            payload=payload,
        )
        payload["trust_record_hash"] = record.integrity_hash
        payload["events"] = all_events
        return payload

    def _sync_pair(self, canonical: Path, working: Path) -> list[dict[str, str]]:
        events: list[dict[str, str]] = []
        canonical_files = self._index_files(canonical)
        working_files = self._index_files(working)

        for name, source in canonical_files.items():
            target = working / name
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                events.append({"event": "restored-working-file", "file": name})
            elif self._digest(source) != self._digest(target):
                shutil.copy2(source, target)
                events.append({"event": "corrected-working-file", "file": name})

        for name, source in working_files.items():
            target = canonical / name
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                events.append({"event": "rehydrated-canonical-file", "file": name})
        return events

    def _index_files(self, root: Path) -> dict[str, Path]:
        return {str(path.relative_to(root)): path for path in root.rglob("*") if path.is_file()}

    def _digest(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()
