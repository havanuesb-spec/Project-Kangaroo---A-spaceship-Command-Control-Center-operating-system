# Pattern Learning

This package learns usage patterns from routed intent activity and predicts likely next moves.

Components:
- `memory.py`: appends usage events and maintains a lightweight summary.
- `predictor.py`: predicts the most likely next intent and routing target from recent history.
- `automation_planner.py`: proposes automation workflows when repeated intent/target patterns emerge.
- `engineering_log.py`: stores calculated intent traces for engineering analysis.
- `engine.py`: observes routed intent activity and returns a prediction snapshot.

Notes:
- this supports progressive automation planning.
- it proposes automation candidates instead of silently taking over work.
