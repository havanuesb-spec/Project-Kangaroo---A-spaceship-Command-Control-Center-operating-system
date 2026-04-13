from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

from identity.avatar.engine import AvatarEngine
from identity.crystal_tree.engine import CrystalTreeEngine

ROOT = Path(r"C:\Multiverse")
OPERATOR_ROOT = Path(__file__).resolve().parent
OUT_FILE = OPERATOR_ROOT / "operator_dashboard.html"

SOURCES = {
    "intent_field_snapshot": ROOT / "intent" / "field_monitor" / "state" / "intent_field_snapshot.json",
    "pattern_summary": ROOT / "intent" / "pattern_learning" / "memory" / "usage_summary.json",
    "coherence_flag": ROOT / "security" / "state" / "coherence_flag.json",
    "biometric_flag": ROOT / "security" / "state" / "biometric_flag.json",
}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "not_found", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"status": "invalid_json", "path": str(path)}


def _card(title: str, payload: dict[str, Any]) -> str:
    pretty = escape(json.dumps(payload, indent=2))
    return f"""
    <section class="card">
      <h2>{escape(title)}</h2>
      <pre>{pretty}</pre>
    </section>
    """


def _build_trajectory_snapshot() -> dict[str, Any]:
    engine = CrystalTreeEngine()
    root = engine.build_from_dimension_registry()
    return engine.calculate_trajectory(
        root=root,
        source_address="dimension://identity/primary",
        target_address="dimension://intent/primary",
    )


def _build_avatar_snapshot() -> dict[str, Any]:
    engine = AvatarEngine()
    return engine.build_presence_profile()


def build_operator_dashboard() -> Path:
    data = {name: _read_json(path) for name, path in SOURCES.items()}
    data["trajectory_snapshot"] = _build_trajectory_snapshot()
    data["avatar_snapshot"] = _build_avatar_snapshot()
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Operator Dashboard</title>
  <style>
    :root {{
      --bg: #f3efe6;
      --panel: #fffaf2;
      --ink: #142033;
      --accent: #b94f2d;
      --line: #d7c9b7;
    }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(185,79,45,0.16), transparent 34%),
        linear-gradient(180deg, #f7f1e7 0%, var(--bg) 100%);
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    header {{
      margin-bottom: 22px;
      padding: 20px 22px;
      border: 1px solid var(--line);
      background: linear-gradient(135deg, rgba(255,250,242,0.98), rgba(244,232,214,0.88));
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 34px;
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }}
    .subtitle {{
      font-size: 15px;
      max-width: 740px;
      line-height: 1.45;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 16px;
      box-shadow: 0 16px 30px rgba(20,32,51,0.06);
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 16px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--accent);
    }}
    pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 12px;
      line-height: 1.45;
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Operator Dashboard</h1>
      <div class="subtitle">
        Oversight surface for intent-field stability, automation emergence, coherence guard state,
        biometric-guard state, crystal-tree trajectory, and avatar presence based on the current
        repo-generated outputs.
      </div>
    </header>
    <div class="grid">
      {_card("Intent Field Snapshot", data["intent_field_snapshot"])}
      {_card("Pattern Summary", data["pattern_summary"])}
      {_card("Coherence Flag", data["coherence_flag"])}
      {_card("Biometric Flag", data["biometric_flag"])}
      {_card("Trajectory Snapshot", data["trajectory_snapshot"])}
      {_card("Avatar Presence", data["avatar_snapshot"])}
    </div>
  </main>
</body>
</html>
"""
    OUT_FILE.write_text(html, encoding="utf-8")
    return OUT_FILE


if __name__ == "__main__":
    print(build_operator_dashboard())
