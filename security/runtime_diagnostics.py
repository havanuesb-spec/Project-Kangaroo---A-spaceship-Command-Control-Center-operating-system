from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib

from intent.field_monitor.memory import SNAPSHOT_FILE, TIMELINE_FILE
from security.biometric_guard import BiometricFlagGuard
from security.flag_guard import CoherenceGuard
from security.transistor_resistor import TransistorResistor
from security.reverse_nanoclocked import ReverseNanoclocked
from trust.trust_registry import TrustRegistry

STATE_DIR = Path(__file__).resolve().parent / "state"
REGULATORY_MOBILE_FILE = STATE_DIR / "regulatory_mobile.json"
LOCK_GATE_FILE = STATE_DIR / "gate_lock.json"
ARMOR_PHRASE = "brinks armored transistor deuto veli"


class SignalGateLock:
    """Lock state for the outside-to-innermost gate.

    The gate remains locked until a verified combination signal is received.
    Signal verification is only possible when the transistor/resistor is active-online.
    The passkey is derived from trust registry records.
    This implements the passkey logic for the transistor/sensor,
    transmitter/tensor, LED overlay remask, and divulgement signal.
    """

    def __init__(self, trust_registry: TrustRegistry | None = None) -> None:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.transistor = TransistorResistor()
        self.trust_registry = trust_registry or TrustRegistry()
        self._ensure_gate_state()

    def _ensure_gate_state(self) -> None:
        if not LOCK_GATE_FILE.exists():
            LOCK_GATE_FILE.write_text(
                json.dumps(
                    {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "locked": True,
                        "passkey_hash": None,
                        "armored_mode": False,
                        "required_fields": [
                            "photon_signal",
                            "sensor_signature",
                            "transmitter_tensor",
                            "led_overlay_mask",
                            "passkey_divulgement",
                        ],
                        "last_attempt": None,
                        "notes": "Gate lock initialized. External access remains locked until a combination signal is verified.",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

    def _read_state(self) -> dict[str, Any]:
        try:
            return json.loads(LOCK_GATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"locked": True, "passkey_hash": None}

    def _write_state(self, payload: dict[str, Any]) -> None:
        LOCK_GATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _normalize(self, value: str) -> str:
        return value.strip().lower()

    def _build_passkey_hash(
        self,
        photon_signal: str,
        sensor_signature: str,
        transmitter_tensor: str,
        led_overlay_mask: str,
        passkey_divulgement: str,
    ) -> str:
        payload = {
            "photon_signal": self._normalize(photon_signal),
            "sensor_signature": self._normalize(sensor_signature),
            "transmitter_tensor": self._normalize(transmitter_tensor),
            "led_overlay_mask": self._normalize(led_overlay_mask),
            "passkey_divulgement": self._normalize(passkey_divulgement),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def set_passkey(
        self,
        photon_signal: str,
        sensor_signature: str,
        transmitter_tensor: str,
        led_overlay_mask: str,
        passkey_divulgement: str,
        armored_mode: bool = False,
    ) -> str:
        """Register passkey in trust registry."""
        passkey_hash = self._build_passkey_hash(
            photon_signal,
            sensor_signature,
            transmitter_tensor,
            led_overlay_mask,
            passkey_divulgement,
        )
        self.trust_registry.issue_record(
            record_type="signal-gate-passkey",
            source="SignalGateLock",
            payload={
                "passkey_hash": passkey_hash,
                "armored_mode": armored_mode,
                "configured_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return passkey_hash

    def verify_passkey(
        self,
        photon_signal: str,
        sensor_signature: str,
        transmitter_tensor: str,
        led_overlay_mask: str,
        passkey_divulgement: str,
    ) -> bool:
        state = self._read_state()

        if not self.transistor.signal_path_active():
            state["last_attempt"] = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "attempt_hash": "rejected",
                "match": False,
                "reason": "transistor-insulated-signal-path-inactive",
                "armored_mode": state.get("armored_mode", False),
            }
            self._write_state(state)
            return False

        expected = self._get_passkey_from_trust()
        candidate = self._build_passkey_hash(
            photon_signal,
            sensor_signature,
            transmitter_tensor,
            led_overlay_mask,
            passkey_divulgement,
        )
        validated = expected is not None and candidate == expected

        state["last_attempt"] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "attempt_hash": candidate,
            "match": validated,
            "source": "trust-registry",
        }
        self._write_state(state)

        if validated:
            self.trust_registry.issue_record(
                record_type="signal-gate-verification",
                source="SignalGateLock",
                payload={
                    "verified": True,
                    "timestamp": state["last_attempt"]["timestamp"],
                },
            )
        return validated

    def unlock_with_signal(
        self,
        photon_signal: str,
        sensor_signature: str,
        transmitter_tensor: str,
        led_overlay_mask: str,
        passkey_divulgement: str,
    ) -> bool:
        if self.verify_passkey(
            photon_signal,
            sensor_signature,
            transmitter_tensor,
            led_overlay_mask,
            passkey_divulgement,
        ):
            state = self._read_state()
            state["locked"] = False
            state["unlocked_at"] = datetime.now(timezone.utc).isoformat()
            self._write_state(state)
            return True
        return False

    def lock(self, reason: str = "runtime-protection") -> None:
        state = self._read_state()
        state["locked"] = True
        state["lock_reason"] = reason
        state["locked_at"] = datetime.now(timezone.utc).isoformat()
        self._write_state(state)

    def get_status(self) -> dict[str, Any]:
        state = self._read_state()
        state["locked"] = bool(state.get("locked", True))
        return state


class RuntimeActiveMediation:
    """Runtime diagnostics and active mediation for Project: Kangaroo."""

    def __init__(self, trust_registry: TrustRegistry | None = None) -> None:
        self.trust_registry = trust_registry or TrustRegistry()
        self.coherence_guard = CoherenceGuard(self.trust_registry)
        self.biometric_guard = BiometricFlagGuard(self.trust_registry)
        self.gate_lock = SignalGateLock(self.trust_registry)
        self.reverse_nanoclocked = ReverseNanoclocked()
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_regulatory_mobile()

    def _ensure_regulatory_mobile(self) -> None:
        if not REGULATORY_MOBILE_FILE.exists():
            REGULATORY_MOBILE_FILE.write_text(
                json.dumps(
                    {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "status": "initialized",
                        "description": "Regulatory mobile mediation runtime anchor.",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {"missing": True}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"invalid_json": True, "path": str(path)}

    def _read_timeline(self) -> list[dict[str, Any]]:
        if not TIMELINE_FILE.exists():
            return []
        timeline: list[dict[str, Any]] = []
        for line in TIMELINE_FILE.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                timeline.append(json.loads(line))
            except json.JSONDecodeError:
                timeline.append({"invalid_line": line})
        return timeline

    def _summarize_timeline(self, timeline: list[dict[str, Any]]) -> dict[str, Any]:
        event_counts = Counter()
        for entry in timeline:
            if isinstance(entry, dict):
                event = entry.get("state") or entry.get("event") or "unknown"
                event_counts[event] += 1
        return {
            "timeline_length": len(timeline),
            "events_by_type": dict(event_counts),
            "most_common_event": event_counts.most_common(1)[0] if event_counts else None,
        }

    def _evaluate_risks(
        self,
        coherence_payload: dict[str, Any],
        biometric_payload: dict[str, Any],
        intent_snapshot: dict[str, Any],
        timeline_summary: dict[str, Any],
        gate_report: dict[str, Any],
    ) -> dict[str, Any]:
        freeze_risk = False
        bottleneck_risk = False
        monopolization_risk = False
        lockdown_risk = gate_report.get("locked", True)

        if intent_snapshot.get("field_status") == "unknown" or timeline_summary["timeline_length"] == 0:
            freeze_risk = True

        if timeline_summary["timeline_length"] > 50 or len(timeline_summary["events_by_type"]) > 10:
            bottleneck_risk = True

        most_common = timeline_summary.get("most_common_event")
        if most_common and most_common[1] / max(1, timeline_summary["timeline_length"]) > 0.8:
            monopolization_risk = True

        if coherence_payload.get("tamper_detected") or biometric_payload.get("tamper_detected"):
            bottleneck_risk = True

        if gate_report.get("locked"):
            freeze_risk = True

        return {
            "freeze_risk": freeze_risk,
            "bottleneck_risk": bottleneck_risk,
            "monopolization_risk": monopolization_risk,
            "lockdown_risk": lockdown_risk,
            "heuristic_details": {
                "coherence_events": len(coherence_payload.get("events", [])),
                "biometric_events": len(biometric_payload.get("events", [])),
                "intent_timeline_length": timeline_summary["timeline_length"],
                "gate_locked": gate_report.get("locked", True),
            },
        }

    def _write_regulatory_mobile(self, report: dict[str, Any]) -> None:
        REGULATORY_MOBILE_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")

    def run(self) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        time_valid = self.reverse_nanoclocked.invalidate_if_reversed(timestamp)

        coherence_report = self.coherence_guard.inspect_and_restore()
        biometric_report = self.biometric_guard.inspect_and_restore()
        gate_report = self.gate_lock.get_status()
        transistor_status = self.gate_lock.transistor.get_status()
        intent_snapshot = self._read_json(SNAPSHOT_FILE)
        timeline = self._read_timeline()
        timeline_summary = self._summarize_timeline(timeline)
        nanoclocked_status = self.reverse_nanoclocked.get_status()

        risks = self._evaluate_risks(
            coherence_payload=coherence_report,
            biometric_payload=biometric_report,
            intent_snapshot=intent_snapshot,
            timeline_summary=timeline_summary,
            gate_report=gate_report,
        )

        report = {
            "timestamp": timestamp,
            "time_valid": time_valid,
            "coherence_report": coherence_report,
            "biometric_report": biometric_report,
            "transistor_status": transistor_status,
            "gate_report": gate_report,
            "nanoclocked_status": nanoclocked_status,
            "intent_snapshot": intent_snapshot,
            "intent_timeline_summary": timeline_summary,
            "risks": risks,
            "regulatory_mobile_path": str(REGULATORY_MOBILE_FILE),
            "gate_lock_path": str(LOCK_GATE_FILE),
        }

        self._write_regulatory_mobile(report)
        record = self.trust_registry.issue_record(
            record_type="runtime-active-mediation",
            source="RuntimeActiveMediation",
            payload=report,
        )
        report["trust_record_hash"] = record.integrity_hash
        return report
