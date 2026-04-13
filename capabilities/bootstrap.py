from __future__ import annotations

import json

from capabilities.processor import MultiverseProcessor


def main() -> None:
    prompt = "Solve a matrix determinant and eigenvalue workflow for a dynamic 11D model."
    result = MultiverseProcessor().process(prompt)
    print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    main()
