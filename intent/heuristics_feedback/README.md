# Heuristics and Feedback

This package adds human-readable intent heuristics and coherence scoring.

Components:
- `coherence_heuristics.py`: contradiction, evidence, and signal-distortion heuristics.
- `memory.py`: feedback event storage.
- `engine.py`: evaluation entry point with trust recording.
- `erasable_program/`: canonical and working content monitored by security.

Important:
- the scoring output is a `distortion_risk`, not a certainty of lying.
- use it for review, prioritization, reconstruction, and anomaly detection.
