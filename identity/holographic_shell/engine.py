from __future__ import annotations

from dataclasses import asdict
from typing import Any

from identity.holographic_shell.models import HolographicWindow


class HolographicShellEngine:
    def compose_window(
        self,
        window_id: str,
        title: str,
        theme: str = "crystalline-amber",
        orbit: str = "primary",
        interoperability_mode: str = "mesh-linked",
        traits: list[str] | None = None,
    ) -> dict[str, Any]:
        window = HolographicWindow(
            window_id=window_id,
            title=title,
            theme=theme,
            orbit=orbit,
            interoperability_mode=interoperability_mode,
            traits=traits or ["holographic", "rotational", "branch-aware"],
        )
        return asdict(window)

    def build_shell_state(self) -> dict[str, Any]:
        windows = [
            self.compose_window("shell-home", "Home Field", orbit="primary"),
            self.compose_window("shell-intent", "Intent Field", orbit="secondary"),
            self.compose_window("shell-logistics", "Logistics View", orbit="peripheral"),
        ]
        return {
            "shell_mode": "holographic-crystal",
            "window_count": len(windows),
            "windows": windows,
        }
