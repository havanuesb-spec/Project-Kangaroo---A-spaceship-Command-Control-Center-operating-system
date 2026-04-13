from __future__ import annotations

import json

from intent.router import IntentRouter


def main() -> None:
    raw_input = "Solve a matrix equation and harvest the result into the capability layer."
    routed = IntentRouter().route(raw_input)
    print(json.dumps(routed, indent=2))


if __name__ == "__main__":
    main()
