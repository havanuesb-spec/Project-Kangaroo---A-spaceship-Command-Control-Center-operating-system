"""
Transistor/Resistor (Insulated-ActiveOnline) State Management

Tracks the operational state of the signal path transistor/resistor circuit element.
While insulated, the gate remains isolated from external signals.
When active-online, the gate accepts signal/passkey verification.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_DIR = Path(__file__).resolve().parent / "state"
TRANSISTOR_STATE_FILE = STATE_DIR / "transistor_resistor.json"


class TransistorResistor:
    """Manages the operational state of the signal path transistor/resistor element."""

    def __init__(self) -> None:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_state_file()

    def _ensure_state_file(self) -> None:
        if not TRANSISTOR_STATE_FILE.exists():
            TRANSISTOR_STATE_FILE.write_text(
                json.dumps(
                    {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "operational_state": "insulated",
                        "modes": {
                            "insulated": {
                                "description": "Transistor is insulated, gate isolated from external signals",
                                "signal_path_active": False,
                                "accepts_verification": False,
                            },
                            "active_online": {
                                "description": "Transistor is active-online, signal path operational",
                                "signal_path_active": True,
                                "accepts_verification": True,
                            },
                        },
                        "last_transition": None,
                        "transition_history": [],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

    def _read_state(self) -> dict[str, Any]:
        try:
            return json.loads(TRANSISTOR_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"operational_state": "insulated", "signal_path_active": False}

    def _write_state(self, payload: dict[str, Any]) -> None:
        TRANSISTOR_STATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def set_active_online(self, reason: str = "gate-verification-request") -> bool:
        """Transition transistor from insulated to active-online state."""
        state = self._read_state()
        if state.get("operational_state") == "active_online":
            return True

        state["operational_state"] = "active_online"
        state["last_transition"] = {
            "from": "insulated",
            "to": "active_online",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
        }
        if "transition_history" not in state:
            state["transition_history"] = []
        state["transition_history"].append(state["last_transition"])
        self._write_state(state)
        return True

    def set_insulated(self, reason: str = "security-lockdown") -> bool:
        """Transition transistor from active-online to insulated state."""
        state = self._read_state()
        if state.get("operational_state") == "insulated":
            return True

        state["operational_state"] = "insulated"
        state["last_transition"] = {
            "from": "active_online",
            "to": "insulated",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
        }
        if "transition_history" not in state:
            state["transition_history"] = []
        state["transition_history"].append(state["last_transition"])
        self._write_state(state)
        return True

    def is_active_online(self) -> bool:
        """Check if transistor is in active-online state."""
        state = self._read_state()
        return state.get("operational_state") == "active_online"

    def is_insulated(self) -> bool:
        """Check if transistor is in insulated state."""
        state = self._read_state()
        return state.get("operational_state") == "insulated"

    def signal_path_active(self) -> bool:
        """Check if the signal path is operational."""
        return self.is_active_online()

    def get_status(self) -> dict[str, Any]:
        """Get detailed transistor/resistor status."""
        state = self._read_state()
        return {
            "operational_state": state.get("operational_state", "insulated"),
            "signal_path_active": self.signal_path_active(),
            "accepts_verification": self.is_active_online(),
            "last_transition": state.get("last_transition"),
            "transition_count": len(state.get("transition_history", [])),
            "transistor_state_file": str(TRANSISTOR_STATE_FILE),
        }
