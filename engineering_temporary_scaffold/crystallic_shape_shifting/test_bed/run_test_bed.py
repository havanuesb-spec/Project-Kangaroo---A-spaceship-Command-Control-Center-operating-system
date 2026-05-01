from __future__ import annotations

import shutil
from pathlib import Path

from engineering_temporary_scaffold.crystallic_shape_shifting.reorganizer import (
    BUCKETS,
    CrystallicReorganizer,
)


TEST_BED_ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = TEST_BED_ROOT / "runtime"
SOURCE_ROOT = RUNTIME_ROOT / "incoming"
DESTINATION_ROOT = RUNTIME_ROOT / "crystallic_shape_shifting"
STATE_FILE = DESTINATION_ROOT / "state" / "test_bed_plan.json"


def seed_fixture() -> None:
    if RUNTIME_ROOT.exists():
        shutil.rmtree(RUNTIME_ROOT)

    SOURCE_ROOT.mkdir(parents=True, exist_ok=True)
    for bucket in BUCKETS:
        (DESTINATION_ROOT / bucket).mkdir(parents=True, exist_ok=True)

    (SOURCE_ROOT / "Crystal lattice notes.txt").write_text(
        "Facet anchors and lattice symmetry sketch.",
        encoding="utf-8",
    )
    (SOURCE_ROOT / "phase_shift_plan.md").write_text(
        "Transition sequence and reversible hinge timing.",
        encoding="utf-8",
    )
    (SOURCE_ROOT / "safe_natural_resin.txt").write_text(
        "Candidate natural resin and composite blend.",
        encoding="utf-8",
    )
    (SOURCE_ROOT / "prototype_mock.py").write_text(
        "print('prototype harness')\n",
        encoding="utf-8",
    )
    (SOURCE_ROOT / "stress_simulation.json").write_text(
        '{"result": "stable", "mode": "simulation"}\n',
        encoding="utf-8",
    )

    variant_dir = SOURCE_ROOT / "morph_variant_alpha"
    variant_dir.mkdir()
    (variant_dir / "README.md").write_text(
        "Expandable body-plan notes.",
        encoding="utf-8",
    )


def print_tree(root: Path) -> None:
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        suffix = "/" if path.is_dir() else ""
        print(f"  - {relative}{suffix}")


def main() -> int:
    seed_fixture()

    reorganizer = CrystallicReorganizer(
        source_root=SOURCE_ROOT,
        destination_root=DESTINATION_ROOT,
        state_file=STATE_FILE,
    )

    dry_run_plan = reorganizer.build_plan()
    reorganizer.write_state(dry_run_plan, apply=False)
    print("[DRY RUN] Planned moves")
    for move in dry_run_plan:
        print(f"  - {Path(move.source).name} -> {Path(move.destination).relative_to(DESTINATION_ROOT)}")

    applied_plan = reorganizer.apply_plan(dry_run_plan)
    reorganizer.write_state(applied_plan, apply=True)
    print("\n[APPLY] Runtime tree")
    print_tree(DESTINATION_ROOT)
    print(f"\nState file: {STATE_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
