"""
Engineering Fractions Command Interface

Provides command-line access to transform complex operations into manageable fractions
and distribute them across time for balanced execution.
"""

from __future__ import annotations

import sys
import json
from datetime import datetime, timezone
from engineering_temporary_scaffold.fractions_transformer import EngineeringFractionsTransformer


def transform_operation(
    operation_id: str,
    description: str,
    complexity: float,
    num_fractions: int,
    duration_ms: int,
) -> None:
    """Transform an operation into manageable fractions."""
    transformer = EngineeringFractionsTransformer()
    fractions = transformer.transform_operation(
        operation_id=operation_id,
        description=description,
        complexity_level=complexity,
        total_fractions=num_fractions,
        estimated_total_duration_ms=duration_ms,
    )
    print(f"\n✓ Transformed '{description}' into {len(fractions)} fractions")
    print(f"  Complexity Level: {complexity}")
    print(f"  Total Duration: {duration_ms}ms")
    print(f"  Fractions Created: {num_fractions}\n")


def schedule_fractions(operation_id: str) -> None:
    """Schedule fractions for time-distributed execution."""
    transformer = EngineeringFractionsTransformer()
    manifest = transformer._read_manifest()
    
    if operation_id not in manifest["operations"]:
        print(f"✗ Operation {operation_id} not found")
        return
    
    op_data = manifest["operations"][operation_id]
    fractions_data = op_data.get("fractions", [])
    
    if not fractions_data:
        print(f"✗ No fractions found for operation {operation_id}")
        return
    
    fractions = [
        type("Fraction", (), f)() for f in fractions_data
    ]
    schedule = transformer.schedule_fractions(fractions)
    
    print(f"\n✓ Scheduled {len(schedule)} fractions for operation: {operation_id}")
    for idx, scheduled in schedule.items():
        print(f"  Fraction {idx + 1}: {scheduled['scheduled_start']} → {scheduled['scheduled_end']}")
    print()


def operation_status(operation_id: str) -> None:
    """Display status of a transformed operation."""
    transformer = EngineeringFractionsTransformer()
    status = transformer.get_operation_status(operation_id)
    
    if "error" in status:
        print(f"✗ {status['error']}")
        return
    
    print(f"\nOperation Status: {operation_id}")
    print(f"  Description: {status['description']}")
    print(f"  Total Fractions: {status['total_fractions']}")
    print(f"  Completed: {status['completed_fractions']}")
    print(f"  Progress: {status['progress_percentage']:.1f}%")
    print(f"  Complexity: {status['complexity_level']}")
    print()


def all_operations() -> None:
    """Display all transformed operations."""
    transformer = EngineeringFractionsTransformer()
    summary = transformer.get_all_operations()
    
    print(f"\nEngineering Fractions Summary:")
    print(f"  Total Operations: {summary['total_operations']}")
    print(f"  Total Fractions: {summary['total_fractions']}\n")
    
    if summary['operations']:
        for op_id, op_data in summary['operations'].items():
            print(f"  {op_id}")
            print(f"    Description: {op_data['description']}")
            print(f"    Fractions: {op_data['completed']}/{op_data['total_fractions']}")
            print(f"    Progress: {op_data['progress']:.1f}%\n")
    else:
        print("  No operations found\n")


def main() -> int:
    """Command interface for engineering fractions management."""
    if len(sys.argv) < 2:
        print("Usage: python -m engineering_temporary_scaffold.fractions_commands <command> [args...]")
        print("\nCommands:")
        print("  transform <id> <description> <complexity> <fractions> <duration_ms>")
        print("    Transform operation into manageable fractions")
        print("  schedule <operation_id>")
        print("    Schedule fractions for time-distributed execution")
        print("  status <operation_id>")
        print("    Display operation status and progress")
        print("  all")
        print("    Display all transformed operations")
        return 1

    command = sys.argv[1].lower()

    if command == "transform" and len(sys.argv) >= 7:
        try:
            transform_operation(
                operation_id=sys.argv[2],
                description=sys.argv[3],
                complexity=float(sys.argv[4]),
                num_fractions=int(sys.argv[5]),
                duration_ms=int(sys.argv[6]),
            )
            return 0
        except Exception as e:
            print(f"✗ Error: {e}")
            return 1
    elif command == "schedule" and len(sys.argv) >= 3:
        schedule_fractions(sys.argv[2])
        return 0
    elif command == "status" and len(sys.argv) >= 3:
        operation_status(sys.argv[2])
        return 0
    elif command == "all":
        all_operations()
        return 0
    else:
        print(f"✗ Unknown command or missing arguments: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
