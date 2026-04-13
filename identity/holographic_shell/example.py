from __future__ import annotations

import json

from identity.holographic_shell.engine import HolographicShellEngine


def main() -> None:
    engine = HolographicShellEngine()
    print(json.dumps(engine.build_shell_state(), indent=2))


if __name__ == "__main__":
    main()
