from __future__ import annotations

import json

from identity.crystal_tree.engine import CrystalTreeEngine


def main() -> None:
    engine = CrystalTreeEngine()
    root = engine.build_from_dimension_registry()
    trajectory = engine.calculate_trajectory(
        root,
        source_address="dimension://identity/primary",
        target_address="dimension://intent/primary",
    )
    print(json.dumps(trajectory, indent=2))


if __name__ == "__main__":
    main()
