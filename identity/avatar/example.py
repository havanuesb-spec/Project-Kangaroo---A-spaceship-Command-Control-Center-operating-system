from __future__ import annotations

import json

from identity.avatar.engine import AvatarEngine


def main() -> None:
    engine = AvatarEngine()
    print(json.dumps(engine.build_presence_profile(), indent=2))


if __name__ == "__main__":
    main()
