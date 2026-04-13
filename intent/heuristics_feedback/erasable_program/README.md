# Erasable Program

This folder stores canonical templates and monitored working files for the
heuristics and feedback subsystem.

Rules:
- `canonical/` holds the source-of-truth files.
- `working/` holds the live editable copies.
- the security guard compares both sides and restores missing or changed files.
- restoration is symmetric so canonical and working copies can be rehydrated.

Important:
- this mechanism restores expected content after tamper or erase events.
- it does not determine human truth directly.
- it supports a coherence workflow based on consistency, distortion, and reconstruction signals.
