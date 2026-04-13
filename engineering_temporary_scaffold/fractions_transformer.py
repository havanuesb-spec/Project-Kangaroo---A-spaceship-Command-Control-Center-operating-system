"""
Engineering Fractions Transformation & Time Distribution

Transforms complex engineering operations into manageable fractions and distributes
them across time periods for balanced execution and resource allocation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ENGINEERING_ROOT = Path(__file__).resolve().parent
FRACTIONS_DIR = ENGINEERING_ROOT / "fractions_state"
FRACTIONS_DIR.mkdir(parents=True, exist_ok=True)
FRACTIONS_MANIFEST = FRACTIONS_DIR / "fractions_manifest.json"


@dataclass
class EngineeringFraction:
    """Represents a manageable fraction of an engineering operation."""

    operation_id: str
    fraction_index: int
    total_fractions: int
    description: str
    complexity_level: float  # 0.0 to 1.0
    estimated_duration_ms: int
    assigned_time_window: str  # ISO 8601 duration format
    status: str = "pending"  # pending, executing, completed, failed
    created_at: str = ""
    started_at: str | None = None
    completed_at: str | None = None

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class EngineeringFractionsTransformer:
    """Transforms complex engineering operations into manageable fractions across time."""

    def __init__(self) -> None:
        FRACTIONS_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_manifest()

    def _ensure_manifest(self) -> None:
        if not FRACTIONS_MANIFEST.exists():
            FRACTIONS_MANIFEST.write_text(
                json.dumps(
                    {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "total_operations": 0,
                        "total_fractions": 0,
                        "operations": {},
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

    def _read_manifest(self) -> dict[str, Any]:
        try:
            return json.loads(FRACTIONS_MANIFEST.read_text(encoding="utf-8"))
        except Exception:
            return {"operations": {}, "total_operations": 0, "total_fractions": 0}

    def _write_manifest(self, manifest: dict[str, Any]) -> None:
        FRACTIONS_MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def transform_operation(
        self,
        operation_id: str,
        description: str,
        complexity_level: float,
        total_fractions: int,
        estimated_total_duration_ms: int,
    ) -> list[EngineeringFraction]:
        """
        Transform a complex operation into manageable fractions distributed across time.

        Args:
            operation_id: Unique operation identifier
            description: Operation description
            complexity_level: 0.0 (simple) to 1.0 (complex)
            total_fractions: Number of fractions to split into
            estimated_total_duration_ms: Total estimated duration

        Returns:
            List of EngineeringFraction objects
        """
        fractions: list[EngineeringFraction] = []
        fraction_duration = estimated_total_duration_ms // total_fractions
        adjusted_complexity = min(1.0, max(0.0, complexity_level))

        for fraction_index in range(total_fractions):
            duration_variance = int(fraction_duration * adjusted_complexity * 0.1)
            adjusted_duration = fraction_duration + (duration_variance if fraction_index % 2 == 0 else -duration_variance)

            time_window = f"PT{max(0, adjusted_duration)}MS"

            fraction = EngineeringFraction(
                operation_id=operation_id,
                fraction_index=fraction_index,
                total_fractions=total_fractions,
                description=f"{description} (fraction {fraction_index + 1}/{total_fractions})",
                complexity_level=adjusted_complexity,
                estimated_duration_ms=max(1, adjusted_duration),
                assigned_time_window=time_window,
            )
            fractions.append(fraction)

        manifest = self._read_manifest()
        manifest["operations"][operation_id] = {
            "description": description,
            "complexity_level": complexity_level,
            "total_fractions": total_fractions,
            "fractions": [asdict(f) for f in fractions],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        manifest["total_operations"] = len(manifest["operations"])
        manifest["total_fractions"] += total_fractions
        self._write_manifest(manifest)

        return fractions

    def schedule_fractions(
        self,
        fractions: list[EngineeringFraction],
        start_time: datetime | None = None,
    ) -> dict[int, dict[str, Any]]:
        """
        Schedule fractions across time windows with managed distribution.

        Args:
            fractions: List of EngineeringFraction objects
            start_time: Start time for scheduling (defaults to now)

        Returns:
            Dictionary mapping fraction_index to scheduled execution details
        """
        if start_time is None:
            start_time = datetime.now(timezone.utc)

        schedule: dict[int, dict[str, Any]] = {}
        current_time = start_time

        for fraction in fractions:
            duration = timedelta(milliseconds=fraction.estimated_duration_ms)
            end_time = current_time + duration

            schedule[fraction.fraction_index] = {
                "fraction_index": fraction.fraction_index,
                "operation_id": fraction.operation_id,
                "description": fraction.description,
                "scheduled_start": current_time.isoformat(),
                "scheduled_end": end_time.isoformat(),
                "duration_ms": fraction.estimated_duration_ms,
                "complexity_level": fraction.complexity_level,
                "status": "scheduled",
            }
            current_time = end_time

        return schedule

    def get_operation_status(self, operation_id: str) -> dict[str, Any]:
        """Get status of a transformed operation and its fractions."""
        manifest = self._read_manifest()
        if operation_id not in manifest["operations"]:
            return {"error": f"Operation {operation_id} not found"}

        op_data = manifest["operations"][operation_id]
        fractions = op_data.get("fractions", [])
        completed = sum(1 for f in fractions if f.get("status") == "completed")

        return {
            "operation_id": operation_id,
            "description": op_data.get("description"),
            "total_fractions": len(fractions),
            "completed_fractions": completed,
            "progress_percentage": (completed / len(fractions) * 100) if fractions else 0,
            "complexity_level": op_data.get("complexity_level"),
            "created_at": op_data.get("created_at"),
        }

    def get_all_operations(self) -> dict[str, Any]:
        """Get summary of all transformed operations."""
        manifest = self._read_manifest()
        operations_summary = {}
        for op_id, op_data in manifest["operations"].items():
            fractions = op_data.get("fractions", [])
            completed = sum(1 for f in fractions if f.get("status") == "completed")
            operations_summary[op_id] = {
                "description": op_data.get("description"),
                "total_fractions": len(fractions),
                "completed": completed,
                "progress": (completed / len(fractions) * 100) if fractions else 0,
            }
        return {
            "total_operations": manifest["total_operations"],
            "total_fractions": manifest["total_fractions"],
            "operations": operations_summary,
        }
