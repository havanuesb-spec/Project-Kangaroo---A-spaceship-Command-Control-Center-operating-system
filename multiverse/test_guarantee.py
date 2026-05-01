from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path
from uuid import uuid4

from multiverse.guarantee import MultiverseGuarantee


class MultiverseGuaranteeTests(unittest.TestCase):
    def setUp(self) -> None:
        runtime_root = Path(__file__).resolve().parent / "_test_runtime"
        runtime_root.mkdir(parents=True, exist_ok=True)
        self.root = runtime_root / uuid4().hex
        self.root.mkdir(parents=True, exist_ok=True)
        self.report_file = self.root / "reports" / "guarantee.json"

    def tearDown(self) -> None:
        if self.root.exists():
            shutil.rmtree(self.root)

    def test_run_reports_verified_when_all_checks_pass(self) -> None:
        required_file = self.root / "ok.txt"
        required_file.write_text("ok", encoding="utf-8")

        guarantee = MultiverseGuarantee(
            root=self.root,
            report_file=self.report_file,
            path_checks={"required_file": required_file},
            import_checks=["json", "pathlib"],
            artifact_checks={"sample_builder": lambda: {"status": "ok"}},
        )

        report = guarantee.run()

        self.assertEqual(report["overall_status"], "verified")
        self.assertEqual(report["summary"]["failed"], 0)
        self.assertTrue(self.report_file.exists())

    def test_run_reports_degraded_when_checks_fail(self) -> None:
        missing_file = self.root / "missing.txt"

        def broken_builder() -> dict[str, str]:
            raise RuntimeError("builder failed")

        guarantee = MultiverseGuarantee(
            root=self.root,
            report_file=self.report_file,
            path_checks={"missing_file": missing_file},
            import_checks=["missing.module.for.test"],
            artifact_checks={"broken_builder": broken_builder},
        )

        report = guarantee.run()
        payload = json.loads(self.report_file.read_text(encoding="utf-8"))

        self.assertEqual(report["overall_status"], "degraded")
        self.assertEqual(report["summary"]["failed"], 3)
        self.assertEqual(payload["overall_status"], "degraded")


if __name__ == "__main__":
    unittest.main()
