from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from intent.voice.rsa_hash import RSADigestVerifier, digest_text
from trust.trust_registry import TrustRegistry


VOICE_ROOT = Path(__file__).resolve().parent
LIBRARY_ROOT = VOICE_ROOT / "voice_library_registration"
CANONICAL_DIR = LIBRARY_ROOT / "canonical"
WORKING_DIR = LIBRARY_ROOT / "working"
CANONICAL_DIR.mkdir(parents=True, exist_ok=True)
WORKING_DIR.mkdir(parents=True, exist_ok=True)


class VoiceLibraryRegistration:
    def __init__(
        self,
        verifier: RSADigestVerifier | None = None,
        trust_registry: TrustRegistry | None = None,
    ) -> None:
        self.verifier = verifier or RSADigestVerifier()
        self.trust_registry = trust_registry or TrustRegistry()

    def register(
        self,
        voice_id: str,
        voice_signature_source: str,
        private_exponent: int,
        public_exponent: int,
        modulus: int,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        digest = digest_text(voice_signature_source)
        signature = self.verifier.sign_digest(digest, private_exponent, modulus)
        payload = {
            "voice_id": voice_id,
            "digest": digest,
            "signature": signature,
            "public_exponent": public_exponent,
            "modulus": modulus,
            "metadata": metadata or {},
        }
        self._write_pair(f"{voice_id}.json", payload)
        record = self.trust_registry.issue_record(
            record_type="voice-registration",
            source="VoiceLibraryRegistration",
            payload=payload,
        )
        return {"library_entry": voice_id, "trust_record_hash": record.integrity_hash}

    def delete(self, voice_id: str) -> dict[str, Any]:
        removed = []
        for root in (CANONICAL_DIR, WORKING_DIR):
            path = root / f"{voice_id}.json"
            if path.exists():
                path.unlink()
                removed.append(str(path))
        record = self.trust_registry.issue_record(
            record_type="voice-deletion",
            source="VoiceLibraryRegistration",
            payload={"voice_id": voice_id, "removed_paths": removed},
        )
        return {"voice_id": voice_id, "removed_paths": removed, "trust_record_hash": record.integrity_hash}

    def _write_pair(self, name: str, payload: dict[str, Any]) -> None:
        for root in (CANONICAL_DIR, WORKING_DIR):
            (root / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")
