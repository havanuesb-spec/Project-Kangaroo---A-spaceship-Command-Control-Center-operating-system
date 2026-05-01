from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import re
from typing import Any

from capabilities.harvester import CapabilityHarvester
from capabilities.mathematics_identifier import MathematicsAlgorithmIdentifier
from capabilities.mathematics_identifier import MathIdentity
from trust.trust_registry import TrustRegistry


@dataclass
class ProcessingResult:
    input_prompt: str
    identity: dict[str, Any]
    generated_capability: str
    decision: dict[str, Any]
    harvest_result: dict[str, Any]


@dataclass
class ProcessorDecision:
    capability_name: str
    processor_version: str
    prompt_fingerprint: str
    normalized_prompt: str
    generated_at: str
    family: str
    algorithm: str
    confidence: float
    evidence: list[str]
    execution_mode: str
    safeguards: list[str]


class MultiverseProcessor:
    processor_version = "internal-processor.v3"

    def __init__(
        self,
        identifier: MathematicsAlgorithmIdentifier | None = None,
        trust_registry: TrustRegistry | None = None,
        harvester: CapabilityHarvester | None = None,
    ) -> None:
        self.identifier = identifier or MathematicsAlgorithmIdentifier()
        self.trust_registry = trust_registry or TrustRegistry()
        self.harvester = harvester or CapabilityHarvester(self.trust_registry)

    def process(self, prompt: str) -> ProcessingResult:
        normalized_prompt = self._normalize_prompt(prompt)
        identity = self.identifier.identify(normalized_prompt)
        decision = self._build_decision(normalized_prompt, identity)
        generated = self._build_capability_module(identity, decision)

        trust_context = self.trust_registry.issue_record(
            record_type="processor-decision",
            source="MultiverseProcessor",
            payload={
                "prompt": prompt,
                "normalized_prompt": normalized_prompt,
                "family": identity.family,
                "algorithm": identity.algorithm,
                "confidence": identity.confidence,
                "evidence": identity.evidence,
                "decision": asdict(decision),
            },
        )

        harvest = self.harvester.interject_modified_code(
            capability_name=decision.capability_name,
            source_code=generated,
            metadata={
                "derived_from": "MultiverseProcessor",
                "processor_version": self.processor_version,
                "trust_context": trust_context.integrity_hash,
                "prompt_fingerprint": decision.prompt_fingerprint,
            },
        )
        return ProcessingResult(
            input_prompt=prompt,
            identity=asdict(identity),
            generated_capability=decision.capability_name,
            decision=asdict(decision),
            harvest_result=harvest,
        )

    def _normalize_prompt(self, prompt: str) -> str:
        normalized = " ".join(prompt.strip().split())
        if not normalized:
            raise ValueError("prompt must contain at least one non-whitespace character")
        return normalized

    def _build_decision(self, prompt: str, identity: MathIdentity) -> ProcessorDecision:
        capability_name = "_".join(
            [
                self._slug(identity.family),
                self._slug(identity.algorithm),
                self._slug(identity.evidence[0]) if identity.evidence else "unmatched",
            ]
        )
        return ProcessorDecision(
            capability_name=capability_name,
            processor_version=self.processor_version,
            prompt_fingerprint=self._fingerprint(prompt),
            normalized_prompt=prompt,
            generated_at=datetime.now(timezone.utc).isoformat(),
            family=identity.family,
            algorithm=identity.algorithm,
            confidence=identity.confidence,
            evidence=list(identity.evidence),
            execution_mode=self._execution_mode_for(identity),
            safeguards=[
                "input-normalized",
                "capability-name-slugged",
                "trust-record-issued-before-harvest",
                "generated-module-exposes-describe-and-execute",
            ],
        )

    def _execution_mode_for(self, identity: MathIdentity) -> str:
        if identity.confidence >= 0.9:
            return "high-confidence-generation"
        if identity.confidence >= 0.75:
            return "assisted-generation"
        return "review-first-generation"

    def _slug(self, value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
        return slug or "unknown"

    def _fingerprint(self, value: str) -> str:
        import hashlib

        return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]

    def _build_capability_module(self, identity: MathIdentity, decision: ProcessorDecision) -> str:
        return f'''from __future__ import annotations

CAPABILITY_FAMILY = "{identity.family}"
CAPABILITY_ALGORITHM = "{identity.algorithm}"
CAPABILITY_CONFIDENCE = {identity.confidence!r}
CAPABILITY_EVIDENCE = {identity.evidence!r}
PROCESSOR_VERSION = "{decision.processor_version}"
PROMPT_FINGERPRINT = "{decision.prompt_fingerprint}"
EXECUTION_MODE = "{decision.execution_mode}"


def describe() -> dict[str, object]:
    return {{
        "family": CAPABILITY_FAMILY,
        "algorithm": CAPABILITY_ALGORITHM,
        "confidence": CAPABILITY_CONFIDENCE,
        "evidence": CAPABILITY_EVIDENCE,
        "mode": "generated-by-multiverse-processor",
        "processor_version": PROCESSOR_VERSION,
        "prompt_fingerprint": PROMPT_FINGERPRINT,
        "execution_mode": EXECUTION_MODE,
    }}


def execute(payload: dict[str, object] | None = None) -> dict[str, object]:
    return {{
        "status": "ready",
        "execution_mode": EXECUTION_MODE,
        "capability": describe(),
        "payload": payload or {{}},
    }}
'''
