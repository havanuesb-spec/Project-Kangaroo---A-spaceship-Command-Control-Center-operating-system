from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


CRYSTALLIC_ROOT = Path(__file__).resolve().parent
INCOMING_ROOT = CRYSTALLIC_ROOT / "incoming"
STATE_ROOT = CRYSTALLIC_ROOT / "state"
DEFAULT_STATE_FILE = STATE_ROOT / "latest_reorganization_plan.json"

BUCKETS: tuple[str, ...] = (
    "core_geometry",
    "phase_transitions",
    "materials",
    "morphologies",
    "prototypes",
    "simulations",
    "state",
    "references",
)

BUCKET_KEYWORDS: dict[str, set[str]] = {
    "core_geometry": {
        "anchor",
        "core",
        "crystal",
        "crystallic",
        "crystalline",
        "facet",
        "facets",
        "formseed",
        "geometry",
        "lattice",
        "shape",
        "symmetry",
    },
    "phase_transitions": {
        "collapse",
        "expand",
        "hinge",
        "metamorph",
        "phase",
        "shift",
        "shifting",
        "statechange",
        "transition",
        "transform",
        "transformation",
    },
    "materials": {
        "alloy",
        "ceramic",
        "coating",
        "composite",
        "fiber",
        "glass",
        "material",
        "materials",
        "metal",
        "natural",
        "polymer",
        "resin",
        "super",
    },
    "morphologies": {
        "body",
        "bodyplan",
        "edge",
        "facetmap",
        "family",
        "form",
        "morph",
        "morphologies",
        "morphology",
        "topology",
        "variant",
    },
    "prototypes": {
        "assembly",
        "build",
        "experiment",
        "fabricate",
        "fabrication",
        "mock",
        "prototype",
        "rig",
        "rigged",
    },
    "simulations": {
        "animate",
        "animation",
        "deform",
        "deformation",
        "motion",
        "render",
        "sim",
        "simulate",
        "simulation",
        "simulations",
        "stress",
    },
    "state": {
        "history",
        "index",
        "log",
        "manifest",
        "registry",
        "snapshot",
        "state",
        "timeline",
    },
}

EXTENSION_BUCKETS: dict[str, str] = {
    ".csv": "state",
    ".gif": "references",
    ".jpeg": "references",
    ".jpg": "references",
    ".json": "state",
    ".jsonl": "state",
    ".md": "references",
    ".pdf": "references",
    ".png": "references",
    ".rst": "references",
    ".svg": "references",
    ".toml": "state",
    ".txt": "references",
    ".webp": "references",
    ".yaml": "state",
    ".yml": "state",
}

RESERVED_NAMES = set(BUCKETS) | {
    "__init__.py",
    "incoming",
    "README.md",
    "reorganizer.py",
}


@dataclass
class PlannedMove:
    source: str
    destination: str
    bucket: str
    item_type: str
    reason: str
    applied: bool = False


class CrystallicReorganizer:
    def __init__(
        self,
        source_root: Path = INCOMING_ROOT,
        destination_root: Path = CRYSTALLIC_ROOT,
        state_file: Path = DEFAULT_STATE_FILE,
    ) -> None:
        self.source_root = source_root.resolve()
        self.destination_root = destination_root.resolve()
        self.state_file = state_file.resolve()

    def build_plan(self) -> list[PlannedMove]:
        if not self.source_root.exists():
            raise FileNotFoundError(f"Source root does not exist: {self.source_root}")
        if not self.source_root.is_dir():
            raise NotADirectoryError(f"Source root is not a directory: {self.source_root}")

        plan: list[PlannedMove] = []
        for item in self._iter_candidates():
            bucket, reason = self._classify(item)
            destination_dir = self.destination_root / bucket
            destination_path = self._unique_destination(destination_dir / item.name)
            plan.append(
                PlannedMove(
                    source=str(item),
                    destination=str(destination_path),
                    bucket=bucket,
                    item_type="directory" if item.is_dir() else "file",
                    reason=reason,
                )
            )
        return plan

    def apply_plan(self, plan: Iterable[PlannedMove]) -> list[PlannedMove]:
        applied_moves: list[PlannedMove] = []
        for move in plan:
            source = Path(move.source)
            destination = Path(move.destination)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            applied_moves.append(
                PlannedMove(
                    source=move.source,
                    destination=move.destination,
                    bucket=move.bucket,
                    item_type=move.item_type,
                    reason=move.reason,
                    applied=True,
                )
            )
        return applied_moves

    def write_state(self, plan: Iterable[PlannedMove], apply: bool) -> Path:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "mode": "apply" if apply else "dry-run",
            "source_root": str(self.source_root),
            "destination_root": str(self.destination_root),
            "moves": [asdict(move) for move in plan],
        }
        self.state_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return self.state_file

    def _iter_candidates(self) -> Iterable[Path]:
        for item in sorted(self.source_root.iterdir(), key=lambda path: path.name.lower()):
            if item.name.startswith("."):
                continue
            if item.name in RESERVED_NAMES:
                continue
            yield item

    def _classify(self, item: Path) -> tuple[str, str]:
        tokens = self._tokenize(item)
        scored: list[tuple[int, str]] = []
        for bucket, keywords in BUCKET_KEYWORDS.items():
            score = sum(1 for token in tokens if token in keywords)
            if score:
                scored.append((score, bucket))

        if scored:
            score, bucket = max(scored, key=lambda entry: (entry[0], entry[1]))
            return bucket, f"keyword score {score} from tokens {sorted(tokens)}"

        extension_bucket = EXTENSION_BUCKETS.get(item.suffix.lower())
        if extension_bucket:
            return extension_bucket, f"extension fallback for {item.suffix.lower()}"

        return "references", "default reference fallback"

    def _tokenize(self, item: Path) -> set[str]:
        raw = f"{item.stem} {item.name}" if item.is_file() else item.name
        base_tokens = {
            token
            for token in re.split(r"[^a-z0-9]+", raw.lower())
            if token
        }

        expanded_tokens = set(base_tokens)
        for token in list(base_tokens):
            if "transform" in token:
                expanded_tokens.update({"transform", "transformation"})
            if "transition" in token:
                expanded_tokens.add("transition")
            if "morph" in token:
                expanded_tokens.update({"morph", "morphology"})
            if "material" in token:
                expanded_tokens.update({"material", "materials"})
            if "sim" in token:
                expanded_tokens.add("sim")
            if "crystal" in token:
                expanded_tokens.add("crystal")
        return expanded_tokens

    @staticmethod
    def _unique_destination(destination: Path) -> Path:
        if not destination.exists():
            return destination

        counter = 1
        while True:
            candidate = destination.with_name(f"{destination.stem}_{counter}{destination.suffix}")
            if not candidate.exists():
                return candidate
            counter += 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reorganize loose crystallic files and folders into the scaffold branches.",
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=INCOMING_ROOT,
        help="Folder to scan for loose files and folders. Defaults to the incoming drop zone.",
    )
    parser.add_argument(
        "--destination-root",
        type=Path,
        default=CRYSTALLIC_ROOT,
        help="Crystallic hierarchy root where items should be placed.",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=DEFAULT_STATE_FILE,
        help="JSON file that captures the latest dry-run or apply plan.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the planned moves. Without this flag the reorganizer only performs a dry run.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    reorganizer = CrystallicReorganizer(
        source_root=args.source_root,
        destination_root=args.destination_root,
        state_file=args.state_file,
    )
    plan = reorganizer.build_plan()
    final_plan = reorganizer.apply_plan(plan) if args.apply else plan
    state_path = reorganizer.write_state(final_plan, apply=args.apply)

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"[{mode}] Crystallic reorganizer")
    print(f"Source: {reorganizer.source_root}")
    print(f"Destination: {reorganizer.destination_root}")
    print(f"Plan file: {state_path}")

    if not final_plan:
        print("No movable files or folders were found.")
        return 0

    print(f"Planned moves: {len(final_plan)}")
    for move in final_plan:
        print(f"- {move.item_type}: {move.source} -> {move.destination} [{move.bucket}]")
        print(f"  reason: {move.reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
