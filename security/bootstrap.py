from __future__ import annotations

import json

from security.coherence_guard import CoherenceGuard


def main() -> None:
    report = CoherenceGuard().inspect_and_restore()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
