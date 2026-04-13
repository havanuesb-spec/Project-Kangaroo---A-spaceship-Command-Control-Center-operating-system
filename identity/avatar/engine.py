from __future__ import annotations

from dataclasses import asdict
from typing import Any

from identity.avatar.models import AvatarState


class AvatarEngine:
    def compose_avatar(
        self,
        avatar_id: str = "operator-avatar",
        display_name: str = "Operator Presence",
        posture: str = "upright-orbital",
        expression: str = "focused-calm",
        presence_mode: str = "holographic-crystalline",
        linked_dimensions: list[str] | None = None,
        traits: list[str] | None = None,
    ) -> dict[str, Any]:
        avatar = AvatarState(
            avatar_id=avatar_id,
            display_name=display_name,
            posture=posture,
            expression=expression,
            presence_mode=presence_mode,
            linked_dimensions=linked_dimensions or ["Identity", "Perspective", "Intent"],
            traits=traits or ["responsive", "branch-aware", "operator-linked"],
        )
        return asdict(avatar)

    def build_presence_profile(self) -> dict[str, Any]:
        avatar = self.compose_avatar()
        return {
            "avatar": avatar,
            "shell_binding": "identity://shell/holographic",
            "perspective_binding": "dimension://perspective/primary",
            "status": "ready",
        }
