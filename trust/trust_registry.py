from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TRUST_ROOT = Path(__file__).resolve().parent
RECORDS_DIR = TRUST_ROOT / "records"
RECORDS_DIR.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass
class TrustRecord:
    record_type: str
    source: str
    payload: dict[str, Any]
    created_at: str
    integrity_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TrustRegistry:
    def __init__(self, records_dir: Path = RECORDS_DIR) -> None:
        self.records_dir = records_dir
        self.records_dir.mkdir(parents=True, exist_ok=True)

    def issue_record(self, record_type: str, source: str, payload: dict[str, Any]) -> TrustRecord:
        base = {
            "record_type": record_type,
            "source": source,
            "payload": payload,
            "created_at": utc_now(),
        }
        record = TrustRecord(
            record_type=record_type,
            source=source,
            payload=payload,
            created_at=base["created_at"],
            integrity_hash=stable_hash(base),
        )
        self._write_record(record)
        return record

    def _write_record(self, record: TrustRecord) -> None:
        ts = record.created_at.replace(":", "-")
        name = f"{ts}_{record.record_type}_{record.integrity_hash[:12]}.json"
        path = self.records_dir / name
        path.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
