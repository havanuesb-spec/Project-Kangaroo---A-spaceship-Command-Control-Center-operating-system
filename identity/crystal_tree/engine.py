from __future__ import annotations

from dataclasses import asdict
from typing import Any

from dimensions.registry import build_dimension_manifest
from identity.crystal_tree.models import CrystalNode


class CrystalTreeEngine:
    def build_default_tree(self) -> CrystalNode:
        return CrystalNode(
            node_id="root",
            label="Multiverse Root",
            dimension="Identity",
            address="identity://root",
            metadata={"mode": "default"},
            children=[
                CrystalNode(
                    node_id="holo-shell",
                    label="Holographic Shell",
                    dimension="Identity",
                    address="identity://shell/holographic",
                    metadata={"path": r"C:\Multiverse\identity\holographic_shell"},
                ),
                CrystalNode(
                    node_id="theme-engine",
                    label="Theme Engine",
                    dimension="Identity",
                    address="identity://theme/core",
                    metadata={"path": r"C:\Multiverse\identity\theme_engine"},
                ),
                CrystalNode(
                    node_id="crystal-tree",
                    label="Crystal Tree",
                    dimension="Identity",
                    address="identity://tree/core",
                    metadata={"path": r"C:\Multiverse\identity\crystal_tree"},
                ),
                CrystalNode(
                    node_id="interop-matrix",
                    label="Interoperability Matrix",
                    dimension="Identity",
                    address="identity://interop/matrix",
                    metadata={"path": r"C:\Multiverse\identity\interoperability_matrix"},
                ),
            ],
        )

    def build_from_dimension_registry(self) -> CrystalNode:
        manifest = build_dimension_manifest()
        children: list[CrystalNode] = []
        for dimension, payload in manifest.items():
            node_id = dimension.lower().replace(" ", "-")
            address = f"dimension://{node_id}"
            children.append(
                CrystalNode(
                    node_id=node_id,
                    label=dimension,
                    dimension=dimension,
                    address=address,
                    metadata={
                        "status": payload.get("status", "unknown"),
                        "primary_path": payload.get("primary_path", ""),
                        "secondary_path": payload.get("secondary_path", ""),
                    },
                    children=[
                        CrystalNode(
                            node_id=f"{node_id}-primary",
                            label="Primary Path",
                            dimension=dimension,
                            address=f"{address}/primary",
                            metadata={"path": payload.get("primary_path", ""), "role": "primary"},
                        ),
                        CrystalNode(
                            node_id=f"{node_id}-secondary",
                            label="Secondary Path",
                            dimension=dimension,
                            address=f"{address}/secondary",
                            metadata={"path": payload.get("secondary_path", ""), "role": "secondary"},
                        ),
                    ],
                )
            )

        return CrystalNode(
            node_id="dimension-root",
            label="Dimension Crystal Root",
            dimension="Identity",
            address="identity://dimensions/root",
            metadata={"source": "dimension-registry", "branch_count": len(children)},
            children=children,
        )

    def rotate_branches(self, root: CrystalNode, focus_dimension: str) -> dict[str, Any]:
        ordered = sorted(
            root.children,
            key=lambda node: (0 if node.dimension == focus_dimension else 1, node.label.lower()),
        )
        root.children = ordered
        return {
            "focus_dimension": focus_dimension,
            "active_branch_order": [node.label for node in ordered],
            "root": asdict(root),
        }

    def resolve_dimensional_address(self, root: CrystalNode, address: str) -> dict[str, Any] | None:
        if root.address == address:
            return asdict(root)
        for child in root.children:
            if child.address == address:
                return asdict(child)
            for grandchild in child.children:
                if grandchild.address == address:
                    return asdict(grandchild)
        return None

    def resolve_target_path(self, root: CrystalNode, address: str) -> str | None:
        if root.address == address:
            return root.metadata.get("path") or root.metadata.get("primary_path")
        for child in root.children:
            if child.address == address:
                return child.metadata.get("path") or child.metadata.get("primary_path")
            for grandchild in child.children:
                if grandchild.address == address:
                    return grandchild.metadata.get("path")
        return None

    def calculate_trajectory(self, root: CrystalNode, source_address: str, target_address: str) -> dict[str, Any]:
        source_node = self.resolve_dimensional_address(root, source_address)
        target_node = self.resolve_dimensional_address(root, target_address)
        if not source_node or not target_node:
            return {
                "status": "unresolved",
                "source_address": source_address,
                "target_address": target_address,
                "steps": [],
            }

        target_dimension = target_node.get("dimension", "unknown")
        steps = [
            {
                "phase": "source-lock",
                "address": source_address,
                "dimension": source_node.get("dimension"),
            },
            {
                "phase": "dimension-rotation",
                "focus_dimension": target_dimension,
                "active_branch_order": self.rotate_branches(root, target_dimension)["active_branch_order"],
            },
            {
                "phase": "target-resolve",
                "address": target_address,
                "target_path": self.resolve_target_path(root, target_address),
            },
        ]
        return {
            "status": "resolved",
            "source_address": source_address,
            "target_address": target_address,
            "target_dimension": target_dimension,
            "trajectory_length": len(steps),
            "steps": steps,
        }
