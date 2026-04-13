from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CrystalNode:
    node_id: str
    label: str
    dimension: str
    address: str
    metadata: dict[str, Any] = field(default_factory=dict)
    children: list["CrystalNode"] = field(default_factory=list)
