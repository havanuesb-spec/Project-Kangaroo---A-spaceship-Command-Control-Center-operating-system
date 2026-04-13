"""
Reverse Nanoclocked Time-Reversal Detection & Invalidation

Detects when system time moves backwards (indicating tampering or rollback attempts)
and invalidates trust records and operations accordingly.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_DIR = Path(__file__).resolve().parent / "state"
NANOCLOCKED_FILE = STATE_DIR / "reverse_nanoclocked.json"


class ReverseNanoclocked:
    """Detects and prevents time-reversal attacks via backwards timestamp detection."""

    def __init__(self) -> None:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_state_file()

    def _ensure_state_file(self) -> None:
        if not NANOCLOCKED_FILE.exists():
            NANOCLOCKED_FILE.write_text(
                json.dumps(
                    {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "last_valid_timestamp": datetime.now(timezone.utc).isoformat(),
                        "reverse_detections": [],
                        "time_reversal_detected": False,
                        "invalidation_count": 0,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

    def _read_state(self) -> dict[str, Any]:
        try:
            return json.loads(NANOCLOCKED_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {
                "last_valid_timestamp": datetime.now(timezone.utc).isoformat(),
                "time_reversal_detected": False,
            }

    def _write_state(self, payload: dict[str, Any]) -> None:
        NANOCLOCKED_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _parse_iso_timestamp(self, timestamp_str: str) -> datetime:
        """Parse ISO 8601 timestamp safely."""
        try:
            if timestamp_str.endswith("Z"):
                return datetime.fromisoformat(timestamp_str[:-1] + "+00:00")
            elif "+" in timestamp_str or timestamp_str.count("-") > 2:
                return datetime.fromisoformat(timestamp_str)
            else:
                return datetime.fromisoformat(timestamp_str)
        except Exception:
            return datetime.now(timezone.utc)

    def check_timestamp(self, test_timestamp: str | None = None) -> dict[str, Any]:
        """
        Check if the current (or provided) timestamp is valid.

        If time has moved backwards, flag as invalid and increment invalidation counter.
        """
        state = self._read_state()
        current_time = datetime.fromisoformat(
            test_timestamp if test_timestamp else datetime.now(timezone.utc).isoformat()
        )
        last_valid = self._parse_iso_timestamp(state.get("last_valid_timestamp", ""))

        if current_time < last_valid:
            state["time_reversal_detected"] = True
            detection = {
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "last_valid_timestamp": state["last_valid_timestamp"],
                "attempted_timestamp": current_time.isoformat(),
                "time_delta_seconds": (last_valid - current_time).total_seconds(),
            }
            if "reverse_detections" not in state:
                state["reverse_detections"] = []
            state["reverse_detections"].append(detection)
            state["invalidation_count"] = state.get("invalidation_count", 0) + 1
            self._write_state(state)

            return {
                "valid": False,
                "reason": "time-reversal-detected",
                "detection": detection,
                "total_reversals": len(state["reverse_detections"]),
            }
        else:
            state["last_valid_timestamp"] = current_time.isoformat()
            self._write_state(state)

            return {
                "valid": True,
                "reason": "timestamp-valid",
                "current_timestamp": current_time.isoformat(),
                "time_reversal_detected": False,
            }

    def invalidate_if_reversed(self, suspect_timestamp: str) -> bool:
        """
        Returns True if the timestamp is valid (no reversal).
        Returns False if time reversal is detected (operation should be invalidated).
        """
        result = self.check_timestamp(suspect_timestamp)
        return result["valid"]

    def get_status(self) -> dict[str, Any]:
        """Get detailed reverse nanoclocked monitoring status."""
        state = self._read_state()
        return {
            "time_reversal_detected": state.get("time_reversal_detected", False),
            "last_valid_timestamp": state.get("last_valid_timestamp"),
            "total_reversal_detections": len(state.get("reverse_detections", [])),
            "total_invalidations": state.get("invalidation_count", 0),
            "nanoclocked_state_file": str(NANOCLOCKED_FILE),
            "reverse_detections": state.get("reverse_detections", [])[-5:]
            if state.get("reverse_detections")
            else [],
        }

    def reset_timeline(self, authorized: bool = False) -> bool:
        """Reset timeline after authorized recovery (admin-only)."""
        if not authorized:
            return False
        state = self._read_state()
        state["time_reversal_detected"] = False
        state["last_valid_timestamp"] = datetime.now(timezone.utc).isoformat()
        self._write_state(state)
        return True
