from __future__ import annotations

import importlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class GuaranteeCheckResult:
    name: str
    category: str
    status: str
    detail: str


class MultiverseGuarantee:
    """Run bounded verification checks across the Multiverse workspace."""

    def __init__(
        self,
        root: Path | None = None,
        report_file: Path | None = None,
        path_checks: dict[str, Path] | None = None,
        import_checks: list[str] | None = None,
        artifact_checks: dict[str, Callable[[], Any]] | None = None,
    ) -> None:
        self.root = root or Path(__file__).resolve().parent.parent
        self.report_file = report_file or self.root / "multiverse" / "state" / "latest_guarantee_report.json"
        self.path_checks = path_checks or self._default_path_checks()
        self.import_checks = import_checks or self._default_import_checks()
        self.artifact_checks = artifact_checks or self._default_artifact_checks()

    def run(self) -> dict[str, Any]:
        results: list[GuaranteeCheckResult] = []
        results.extend(self._run_path_checks())
        results.extend(self._run_import_checks())
        results.extend(self._run_artifact_checks())

        passed_count = sum(1 for result in results if result.status == "passed")
        failed_count = len(results) - passed_count
        overall_status = "verified" if failed_count == 0 else "degraded"

        report = {
            "generated_at": utc_now(),
            "root": str(self.root),
            "overall_status": overall_status,
            "guarantee_boundary": (
                "bounded verification only; confirms current local paths, imports, "
                "and artifact generation but cannot guarantee future edits or runtime environments"
            ),
            "summary": {
                "total_checks": len(results),
                "passed": passed_count,
                "failed": failed_count,
            },
            "results": [asdict(result) for result in results],
        }
        self._write_report(report)
        return report

    def _default_path_checks(self) -> dict[str, Path]:
        return {
            "main_orchestrator": self.root / "jscjr_multiverse.py",
            "intent_router": self.root / "intent" / "router.py",
            "capability_processor": self.root / "capabilities" / "processor.py",
            "identity_registry": self.root / "identity" / "registry.py",
            "security_runtime_diagnostics": self.root / "security" / "runtime_diagnostics.py",
            "trust_registry": self.root / "trust" / "trust_registry.py",
            "dimension_registry": self.root / "dimensions" / "registry.py",
            "crystallic_reorganizer_exe": self.root / "multiverse" / "tools" / "crystallic_shape_shifting" / "dist" / "CrystallicReorganizer.exe",
        }

    @staticmethod
    def _default_import_checks() -> list[str]:
        return [
            "intent.router",
            "capabilities.processor",
            "identity.registry",
            "security.runtime_diagnostics",
            "trust.trust_registry",
            "dimensions.registry",
            "engineering_temporary_scaffold.builder",
        ]

    def _default_artifact_checks(self) -> dict[str, Callable[[], Any]]:
        return {
            "dimension_manifest_builder": self._build_dimension_manifest,
            "engineering_scaffold_builder": self._build_engineering_scaffold,
        }

    def _run_path_checks(self) -> list[GuaranteeCheckResult]:
        results: list[GuaranteeCheckResult] = []
        for name, path in self.path_checks.items():
            exists = path.exists()
            results.append(
                GuaranteeCheckResult(
                    name=name,
                    category="path",
                    status="passed" if exists else "failed",
                    detail=f"exists at {path}" if exists else f"missing required path {path}",
                )
            )
        return results

    def _run_import_checks(self) -> list[GuaranteeCheckResult]:
        results: list[GuaranteeCheckResult] = []
        for module_name in self.import_checks:
            try:
                importlib.import_module(module_name)
                results.append(
                    GuaranteeCheckResult(
                        name=module_name,
                        category="import",
                        status="passed",
                        detail="module imported successfully",
                    )
                )
            except Exception as exc:
                results.append(
                    GuaranteeCheckResult(
                        name=module_name,
                        category="import",
                        status="failed",
                        detail=f"import failed: {exc}",
                    )
                )
        return results

    def _run_artifact_checks(self) -> list[GuaranteeCheckResult]:
        results: list[GuaranteeCheckResult] = []
        for name, builder in self.artifact_checks.items():
            try:
                artifact = builder()
                results.append(
                    GuaranteeCheckResult(
                        name=name,
                        category="artifact",
                        status="passed",
                        detail=self._describe_artifact(artifact),
                    )
                )
            except Exception as exc:
                results.append(
                    GuaranteeCheckResult(
                        name=name,
                        category="artifact",
                        status="failed",
                        detail=f"artifact check failed: {exc}",
                    )
                )
        return results

    def _build_dimension_manifest(self) -> Any:
        from dimensions.registry import build_dimension_manifest

        return build_dimension_manifest()

    def _build_engineering_scaffold(self) -> Any:
        from engineering_temporary_scaffold.builder import build_engineering_scaffold

        return build_engineering_scaffold()

    @staticmethod
    def _describe_artifact(artifact: Any) -> str:
        if isinstance(artifact, dict):
            return f"builder returned dict with {len(artifact)} entries"
        if artifact is None:
            return "builder completed without returning a value"
        return f"builder returned {type(artifact).__name__}"

    def _write_report(self, report: dict[str, Any]) -> None:
        self.report_file.parent.mkdir(parents=True, exist_ok=True)
        self.report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> int:
    report = MultiverseGuarantee().run()
    logging.basicConfig(level=logging.INFO)
    logger.info(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
