from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

from identity.crystal_tree.engine import CrystalTreeEngine

ROOT = Path(r"C:\Multiverse")
LOGISTICS_ROOT = Path(__file__).resolve().parent
OUT_FILE = LOGISTICS_ROOT / "logistics_dashboard.html"

SOURCES = {
    "field_timeline": ROOT / "intent" / "field_monitor" / "state" / "intent_field_timeline.jsonl",
    "intent_log": ROOT / "intent" / "pattern_learning" / "logs" / "calculated_intent_log.jsonl",
    "memory_draft_entries": ROOT / "intent" / "memory_draft" / "data" / "entries.jsonl",
}


def _read_jsonl_preview(path: Path, limit: int = 5) -> list[dict[str, Any]]:
    if not path.exists():
        return [{"status": "not_found", "path": str(path)}]
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"status": "invalid_json", "path": str(path)})
                break
    return rows


def _card(title: str, payload: list[dict[str, Any]]) -> str:
    pretty = escape(json.dumps(payload, indent=2))
    return f"""
    <section class="card">
      <h2>{escape(title)}</h2>
      <pre>{pretty}</pre>
    </section>
    """


def _build_logistics_trajectory() -> list[dict[str, Any]]:
    engine = CrystalTreeEngine()
    root = engine.build_from_dimension_registry()
    trajectory = engine.calculate_trajectory(
        root=root,
        source_address="dimension://memory/primary",
        target_address="dimension://capability/primary",
    )
    return [trajectory]


def build_logistics_dashboard() -> Path:
    data = {name: _read_jsonl_preview(path) for name, path in SOURCES.items()}
    data["trajectory_flow"] = _build_logistics_trajectory()
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Logistics Counterpart</title>
  <style>
    :root {{
      --bg: #e8f0ec;
      --panel: #f8fcfa;
      --ink: #163126;
      --accent: #2d7c5a;
      --line: #bfd4c7;
    }}
    body {{
      margin: 0;
      font-family: "Trebuchet MS", Verdana, sans-serif;
      color: var(--ink);
      background:
        linear-gradient(135deg, rgba(45,124,90,0.12), transparent 35%),
        linear-gradient(180deg, #eef6f1 0%, var(--bg) 100%);
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
      background: linear-gradient(135deg, rgba(248,252,250,0.98), rgba(222,239,229,0.9));
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 32px;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }}
    .subtitle {{
      font-size: 15px;
      max-width: 760px;
      line-height: 1.45;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 16px;
      box-shadow: 0 16px 30px rgba(22,49,38,0.06);
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
      <h1>Logistics Counterpart</h1>
      <div class="subtitle">
        Flow-oriented view of recent intent-field changes, calculated intent logs, and memory-draft
        movement for engineering, operations logistics, and crystal-tree motion.
      </div>
    </header>
    <div class="grid">
      {_card("Field Timeline Preview", data["field_timeline"])}
      {_card("Calculated Intent Log Preview", data["intent_log"])}
      {_card("Memory Draft Preview", data["memory_draft_entries"])}
      {_card("Trajectory Flow Preview", data["trajectory_flow"])}
    </div>
  </main>
</body>
</html>
"""
    OUT_FILE.write_text(html, encoding="utf-8")
    return OUT_FILE


if __name__ == "__main__":
    print(build_logistics_dashboard())
