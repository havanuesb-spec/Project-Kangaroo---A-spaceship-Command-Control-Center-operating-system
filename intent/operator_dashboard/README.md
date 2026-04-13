# Operator Dashboard

This package builds a static operator-facing dashboard.

Current data sources:
- `intent/field_monitor/state/intent_field_snapshot.json`
- `intent/pattern_learning/memory/usage_summary.json`
- `security/state/coherence_flag.json`
- `security/state/biometric_flag.json`
- `identity/crystal_tree/engine.py` trajectory snapshot
- `identity/avatar/engine.py` avatar presence snapshot

Output:
- `operator_dashboard.html`
