#!/usr/bin/env python3
"""Generate a SHA256 'live' hash for the dimensions registry.

This script writes a new hash to `dimensions/current_hash.txt` each time it runs.
Use scheduling (cron/Task Scheduler/CI) to refresh regularly.
"""
import hashlib
import uuid
import time
from pathlib import Path


def generate_hash() -> str:
    payload = f"{time.time()}|{uuid.uuid4().hex}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main():
    repo_dir = Path(__file__).parent
    out = repo_dir / "current_hash.txt"
    h = generate_hash()
    # atomic write
    tmp = out.with_suffix(".tmp")
    tmp.write_text(h + "\n")
    tmp.replace(out)
    print(h)


if __name__ == "__main__":
    main()
