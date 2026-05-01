from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from capabilities.processor import MultiverseProcessor


def main() -> None:
    prompt = "Solve a matrix determinant and eigenvalue workflow for a dynamic 11D model."
    result = MultiverseProcessor().process(prompt)
    print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    main()
