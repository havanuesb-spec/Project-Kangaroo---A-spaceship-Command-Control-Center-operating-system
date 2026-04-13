from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(r"C:\Multiverse")
SCAFFOLD_ROOT = Path(__file__).resolve().parent
MANIFEST_FILE = SCAFFOLD_ROOT / "engineering_access_manifest.json"
INDEX_FILE = SCAFFOLD_ROOT / "engineering_access_index.md"


TARGETS = {
    "dimensions_root": ROOT / "dimensions",
    "connectors_root": ROOT / "connectors",
    "identity_root": ROOT / "identity",
    "intent_root": ROOT / "intent",
    "operator_dashboard": ROOT / "intent" / "operator_dashboard",
    "logistics_counterpart": ROOT / "intent" / "logistics_counterpart",
    "pattern_learning": ROOT / "intent" / "pattern_learning",
    "field_monitor": ROOT / "intent" / "field_monitor",
    "memory_draft": ROOT / "intent" / "memory_draft",
    "iris": ROOT / "intent" / "iris",
    "voice": ROOT / "intent" / "voice",
    "heuristics_feedback": ROOT / "intent" / "heuristics_feedback",
    "security_root": ROOT / "security",
    "trust_root": ROOT / "trust",
}


def build_engineering_scaffold() -> dict[str, str]:
    manifest = {
        name: str(path)
        for name, path in TARGETS.items()
    }
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    lines = [
        "# Engineering Temporary Scaffold",
        "",
        "This scaffold indexes the main folders engineering may want to revisit.",
        "",
        "## Indexed Paths",
    ]
    for name, path in TARGETS.items():
        lines.append(f"- `{name}`: `{path}`")
    lines.extend(
        [
            "",
            "## Suggested Entry Points",
            f"- Dimension registry: `{ROOT / 'dimensions' / 'registry.py'}`",
            f"- Dimension manifest: `{ROOT / 'dimensions' / 'manifest.json'}`",
            f"- Connectors root: `{ROOT / 'connectors'}`",
            f"- Identity registry root: `{ROOT / 'identity'}`",
            f"- Crystal tree definition: `{ROOT / 'identity' / 'crystal_tree' / 'README.md'}`",
            f"- Holographic shell definition: `{ROOT / 'identity' / 'holographic_shell' / 'README.md'}`",
            f"- Avatar definition: `{ROOT / 'identity' / 'avatar' / 'README.md'}`",
            f"- Intent routing: `{ROOT / 'intent' / 'router.py'}`",
            f"- Operator dashboard builder: `{ROOT / 'intent' / 'operator_dashboard' / 'builder.py'}`",
            f"- Logistics dashboard builder: `{ROOT / 'intent' / 'logistics_counterpart' / 'builder.py'}`",
            f"- Pattern learning engine: `{ROOT / 'intent' / 'pattern_learning' / 'engine.py'}`",
            f"- Field monitor: `{ROOT / 'intent' / 'field_monitor' / 'monitor.py'}`",
            f"- Memory draft engine: `{ROOT / 'intent' / 'memory_draft' / 'engine.py'}`",
            f"- Iris registration (access/trust side): `{ROOT / 'intent' / 'iris' / 'registration.py'}`",
            f"- Iris registration: `{ROOT / 'intent' / 'iris' / 'registration.py'}`",
            f"- Voice registration: `{ROOT / 'intent' / 'voice' / 'registration.py'}`",
            f"- Voice timbre coherence: `{ROOT / 'intent' / 'voice' / 'timbre_coherence.py'}`",
            f"- Coherence guard: `{ROOT / 'security' / 'coherence_guard.py'}`",
            f"- Biometric guard: `{ROOT / 'security' / 'biometric_guard.py'}`",
        ]
    )
    INDEX_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(build_engineering_scaffold(), indent=2))
