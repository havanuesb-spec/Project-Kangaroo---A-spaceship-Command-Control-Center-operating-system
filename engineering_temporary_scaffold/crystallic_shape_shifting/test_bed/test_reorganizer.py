from __future__ import annotations

import json
import shutil
import unittest
from uuid import uuid4
from pathlib import Path

from engineering_temporary_scaffold.crystallic_shape_shifting.reorganizer import (
    BUCKETS,
    CrystallicReorganizer,
)


class CrystallicReorganizerTests(unittest.TestCase):
    def setUp(self) -> None:
        runtime_root = Path(__file__).resolve().parent / "runtime_unittest"
        runtime_root.mkdir(parents=True, exist_ok=True)
        self.root = runtime_root / uuid4().hex
        self.source_root = self.root / "incoming"
        self.destination_root = self.root / "crystallic_shape_shifting"
        self.state_file = self.destination_root / "state" / "test_plan.json"

        self.source_root.mkdir(parents=True, exist_ok=True)
        for bucket in BUCKETS:
            (self.destination_root / bucket).mkdir(parents=True, exist_ok=True)

        (self.source_root / "crystal_geometry.txt").write_text("geometry", encoding="utf-8")
        (self.source_root / "phase_shift_notes.md").write_text("phase", encoding="utf-8")
        (self.source_root / "natural_materials.txt").write_text("materials", encoding="utf-8")
        (self.source_root / "prototype_mock.py").write_text("prototype", encoding="utf-8")
        (self.source_root / "stress_simulation.json").write_text("simulation", encoding="utf-8")
        variant_dir = self.source_root / "morph_variant_alpha"
        variant_dir.mkdir()
        (variant_dir / "README.md").write_text("variant", encoding="utf-8")

    def tearDown(self) -> None:
        if self.root.exists():
            shutil.rmtree(self.root)

    def test_build_plan_classifies_files_and_directories(self) -> None:
        reorganizer = CrystallicReorganizer(
            source_root=self.source_root,
            destination_root=self.destination_root,
            state_file=self.state_file,
        )

        plan = reorganizer.build_plan()
        buckets_by_name = {Path(move.source).name: move.bucket for move in plan}

        self.assertEqual(buckets_by_name["crystal_geometry.txt"], "core_geometry")
        self.assertEqual(buckets_by_name["phase_shift_notes.md"], "phase_transitions")
        self.assertEqual(buckets_by_name["natural_materials.txt"], "materials")
        self.assertEqual(buckets_by_name["prototype_mock.py"], "prototypes")
        self.assertEqual(buckets_by_name["stress_simulation.json"], "simulations")
        self.assertEqual(buckets_by_name["morph_variant_alpha"], "morphologies")

    def test_apply_plan_moves_items_and_writes_state(self) -> None:
        reorganizer = CrystallicReorganizer(
            source_root=self.source_root,
            destination_root=self.destination_root,
            state_file=self.state_file,
        )

        plan = reorganizer.build_plan()
        applied_plan = reorganizer.apply_plan(plan)
        state_path = reorganizer.write_state(applied_plan, apply=True)

        self.assertTrue((self.destination_root / "core_geometry" / "crystal_geometry.txt").exists())
        self.assertTrue((self.destination_root / "phase_transitions" / "phase_shift_notes.md").exists())
        self.assertTrue((self.destination_root / "materials" / "natural_materials.txt").exists())
        self.assertTrue((self.destination_root / "prototypes" / "prototype_mock.py").exists())
        self.assertTrue((self.destination_root / "simulations" / "stress_simulation.json").exists())
        self.assertTrue((self.destination_root / "morphologies" / "morph_variant_alpha").exists())
        self.assertEqual(list(self.source_root.iterdir()), [])

        payload = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["mode"], "apply")
        self.assertTrue(all(move["applied"] for move in payload["moves"]))


if __name__ == "__main__":
    unittest.main()
