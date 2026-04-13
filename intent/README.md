# Multiverse Intent

This folder is the intent layer for the OS direction of the project.

Files:
- `intent_model.py`: base data structures for incoming signals and routed plans.
- `classifier.py`: classifies incoming intent into a system-level plan.
- `router.py`: turns raw input into a routed plan and creates a trust record.
- `bootstrap.py`: example entry point for the intent pipeline.
- `heuristics_feedback/`: contradiction, coherence, and feedback memory subsystem.
- `iris/`: iris registration and RSA-digest access control.
- `voice/`: voice registration, RSA-digest access control, and timbre coherence scoring.
- `pattern_learning/`: usage pattern memory, next-move prediction, and engineering intent logs.
- `field_monitor/`: live intent field stability, drift, and automation-pressure monitoring.
- `memory_draft/`: working memory drafts and trust-backed memory summaries.
- `operator_dashboard/`: operator-facing dashboard builder for current oversight telemetry.
- `logistics_counterpart/`: logistics-oriented dashboard builder for flow and engineering traces.

Recognized OS dimensions are registered under:
- `C:\Multiverse\dimensions`
- `C:\Multiverse\connectors`

Identity shell and crystal-tree scaffolds are under:
- `C:\Multiverse\identity`

Current routing targets:
- `capabilities.processor`
- `capabilities.harvester`
- `trust.trust_registry`
- `intent.router`

Suggested next step:
- connect coherence scans into the router or scheduler so monitored intent assets self-heal continuously.
