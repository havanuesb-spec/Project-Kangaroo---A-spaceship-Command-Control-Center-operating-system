# Intent Field Monitor

This package watches routed intent activity as a field rather than a single event.

Components:
- `analyzer.py`: calculates dominant intent, drift risk, and automation pressure.
- `memory.py`: stores the latest field snapshot and a timeline of field states.
- `monitor.py`: main entry point for updating the intent field after each routed event.

Outputs:
- current dominant intent field
- drift risk across recent events
- automation pressure from repeated patterns
- trust-backed field-monitor records for engineering use
