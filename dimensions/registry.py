from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(r"C:\Multiverse")
DIMENSIONS_ROOT = Path(__file__).resolve().parent
MANIFEST_FILE = DIMENSIONS_ROOT / "manifest.json"


DIMENSIONS = [
    "Identity",
    "Intent",
    "State",
    "Relation",
    "Space",
    "Time",
    "Memory",
    "Capability",
    "Trust",
    "Perspective",
    "Transformation",
]


def build_dimension_manifest() -> dict[str, dict[str, str]]:
    manifest = {
        "Identity": {
            "status": "active",
            "primary_path": str(ROOT / "identity"),
            "secondary_path": str(ROOT / "identity" / "avatar"),
        },
        "Intent": {
            "status": "active",
            "primary_path": str(ROOT / "intent"),
            "secondary_path": str(ROOT / "intent" / "router.py"),
        },
        "State": {
            "status": "partial",
            "primary_path": str(ROOT / "intent" / "field_monitor"),
            "secondary_path": str(ROOT / "security" / "state"),
        },
        "Relation": {
            "status": "pending",
            "primary_path": str(ROOT / "connectors" / "pending" / "relation_connector.md"),
            "secondary_path": str(ROOT / "engineering_temporary_scaffold"),
        },
        "Space": {
            "status": "pending",
            "primary_path": str(ROOT / "connectors" / "pending" / "space_connector.md"),
            "secondary_path": str(ROOT / "engineering_temporary_scaffold"),
        },
        "Time": {
            "status": "pending",
            "primary_path": str(ROOT / "connectors" / "pending" / "time_connector.md"),
            "secondary_path": str(ROOT / "engineering_temporary_scaffold"),
        },
        "Memory": {
            "status": "active",
            "primary_path": str(ROOT / "intent" / "memory_draft"),
            "secondary_path": str(ROOT / "intent" / "pattern_learning"),
        },
        "Capability": {
            "status": "active",
            "primary_path": str(ROOT / "capabilities"),
            "secondary_path": str(ROOT / "capabilities" / "processor.py"),
        },
        "Trust": {
            "status": "active",
            "primary_path": str(ROOT / "trust"),
            "secondary_path": str(ROOT / "trust" / "trust_registry.py"),
        },
        "Perspective": {
            "status": "partial",
            "primary_path": str(ROOT / "intent" / "operator_dashboard"),
            "secondary_path": str(ROOT / "intent" / "logistics_counterpart"),
        },
        "Transformation": {
            "status": "partial",
            "primary_path": str(ROOT / "capabilities" / "harvester.py"),
            "secondary_path": str(ROOT / "intent" / "pattern_learning" / "automation_planner.py"),
        },
    }
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(build_dimension_manifest(), indent=2))
