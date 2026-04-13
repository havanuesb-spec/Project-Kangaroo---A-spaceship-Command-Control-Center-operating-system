# Multiverse Security

This folder monitors and restores the intent heuristics erasable program as a coherence field.

Components:
- `coherence_guard.py`: photonic/coherence-facing guard entry point.
- `flag_guard.py`: checks canonical and working copies and restores missing or changed files.
- `biometric_guard.py`: restores iris and voice registration libraries from canonical copies.
- `transistor_resistor.py`: manages transistor/resistor operational state (insulated vs. active-online).
- `transistor_commands.py`: command module for transistor state transitions.
- `runtime_diagnostics.py`: runtime active mediation diagnostics and regulatory state management.
- `state/coherence_flag.json`: latest scan state.
- `state/biometric_flag.json`: latest biometric scan state.
- `state/gate_lock.json`: outside-to-innermost gate lock state, locked until a validated signal/passkey combination is supplied.
- `state/transistor_resistor.json`: transistor/resistor operational state and transition history.
- `bootstrap.py`: example entry point for a scan-and-restore run.

Behavior:
- if working files are removed or modified, they are restored from canonical files
- if canonical files are missing, they are rehydrated from working files
- every scan emits a trust record

Important:
- this is a self-healing coherence and file integrity mechanism
- it is not proof of human deception by itself
