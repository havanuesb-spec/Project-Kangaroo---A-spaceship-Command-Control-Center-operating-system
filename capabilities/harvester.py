from __future__ import annotations

from pathlib import Path
from typing import Any

from trust.trust_registry import TrustRegistry


CAPABILITIES_ROOT = Path(__file__).resolve().parent
HARVEST_DIR = CAPABILITIES_ROOT / "harvests"
HARVEST_DIR.mkdir(parents=True, exist_ok=True)


class CapabilityHarvester:
    def __init__(self, trust_registry: TrustRegistry | None = None) -> None:
        self.trust_registry = trust_registry or TrustRegistry()

    def interject_modified_code(self, capability_name: str, source_code: str, metadata: dict[str, Any]) -> dict[str, Any]:
        target = HARVEST_DIR / f"{capability_name}.py"
        target.write_text(source_code, encoding="utf-8")

        payload = {
            "capability_name": capability_name,
            "target_path": str(target),
            "metadata": metadata,
            "bytes_written": len(source_code.encode("utf-8")),
        }
        record = self.trust_registry.issue_record(
            record_type="capability-harvest",
            source="CapabilityHarvester",
            payload=payload,
        )
        return {
            "written_to": str(target),
            "trust_record": record.to_dict(),
        }
