from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AvatarState:
    avatar_id: str
    display_name: str
    posture: str
    expression: str
    presence_mode: str
    linked_dimensions: list[str] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
