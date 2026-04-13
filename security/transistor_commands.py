"""
Transistor/Resistor Command Module

Provides command-line interface to manage transistor/resistor state transitions
between insulated and active-online operational modes.
"""

from __future__ import annotations

import sys
from pathlib import Path

from security.transistor_resistor import TransistorResistor


def activate_signal_path(reason: str = "operator-command") -> bool:
    """Transition transistor to active-online state."""
    transistor = TransistorResistor()
    result = transistor.set_active_online(reason=reason)
    status = transistor.get_status()
    print(f"Transistor state: {status['operational_state']}")
    print(f"Signal path active: {status['signal_path_active']}")
    return result


def deactivate_signal_path(reason: str = "operator-command") -> bool:
    """Transition transistor to insulated state."""
    transistor = TransistorResistor()
    result = transistor.set_insulated(reason=reason)
    status = transistor.get_status()
    print(f"Transistor state: {status['operational_state']}")
    print(f"Signal path active: {status['signal_path_active']}")
    return result


def get_transistor_status() -> dict:
    """Get current transistor/resistor operational state."""
    transistor = TransistorResistor()
    status = transistor.get_status()
    print("\nTransistor/Resistor Status:")
    print(f"  Operational State: {status['operational_state']}")
    print(f"  Signal Path Active: {status['signal_path_active']}")
    print(f"  Accepts Verification: {status['accepts_verification']}")
    print(f"  Transition Count: {status['transition_count']}")
    if status['last_transition']:
        print(f"  Last Transition: {status['last_transition']}")
    return status


def main() -> int:
    """Command module interface for transistor/resistor control."""
    if len(sys.argv) < 2:
        print("Usage: python -m security.transistor_commands <command> [reason]")
        print("\nCommands:")
        print("  activate   - Set transistor to active-online (signal path enabled)")
        print("  deactivate - Set transistor to insulated (signal path disabled)")
        print("  status     - Display current transistor state")
        return 1

    command = sys.argv[1].lower()
    reason = sys.argv[2] if len(sys.argv) > 2 else "operator-command"

    if command == "activate":
        return 0 if activate_signal_path(reason) else 1
    elif command == "deactivate":
        return 0 if deactivate_signal_path(reason) else 1
    elif command == "status":
        get_transistor_status()
        return 0
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
