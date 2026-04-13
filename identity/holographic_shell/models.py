from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HolographicWindow:
    window_id: str
    title: str
    theme: str
    orbit: str
    interoperability_mode: str
    traits: list[str] = field(default_factory=list)
