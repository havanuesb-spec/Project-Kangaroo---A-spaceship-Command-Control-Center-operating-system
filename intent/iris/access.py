from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from intent.iris.rsa_hash import RSADigestVerifier, digest_text
from intent.iris.registration import WORKING_DIR
from trust.trust_registry import TrustRegistry


class IrisAccessController:
    def __init__(
        self,
        verifier: RSADigestVerifier | None = None,
        trust_registry: TrustRegistry | None = None,
    ) -> None:
        self.verifier = verifier or RSADigestVerifier()
        self.trust_registry = trust_registry or TrustRegistry()

    def allow_access(self, iris_id: str, iris_signature_source: str) -> dict[str, Any]:
        path = WORKING_DIR / f"{iris_id}.json"
        if not path.exists():
            result = {"allowed": False, "reason": "iris identity not registered"}
        else:
            payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
            digest = digest_text(iris_signature_source)
            ok = self.verifier.verify_digest(
                digest_hex=digest,
                signature=payload["signature"],
                public_exponent=payload["public_exponent"],
                modulus=payload["modulus"],
            )
            result = {
                "allowed": ok,
                "reason": "verified" if ok else "rsa digest mismatch",
                "registered_digest": payload["digest"],
                "presented_digest": digest,
            }

        record = self.trust_registry.issue_record(
            record_type="iris-access-check",
            source="IrisAccessController",
            payload={"iris_id": iris_id, **result},
        )
        result["trust_record_hash"] = record.integrity_hash
        return result
