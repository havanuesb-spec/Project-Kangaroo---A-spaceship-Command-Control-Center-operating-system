from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from capabilities.harvester import CapabilityHarvester
from capabilities.mathematics_identifier import MathematicsAlgorithmIdentifier
from trust.trust_registry import TrustRegistry


@dataclass
class ProcessingResult:
    input_prompt: str
    identity: dict[str, Any]
    generated_capability: str
    harvest_result: dict[str, Any]


class MultiverseProcessor:
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
        identity = self.identifier.identify(prompt)
        capability_name = f"{identity.family.replace('-', '_')}_{identity.algorithm.replace('-', '_')}"
        generated = self._build_capability_module(identity.family, identity.algorithm)

        trust_context = self.trust_registry.issue_record(
            record_type="processor-decision",
            source="MultiverseProcessor",
            payload={
                "prompt": prompt,
                "family": identity.family,
                "algorithm": identity.algorithm,
                "confidence": identity.confidence,
                "evidence": identity.evidence,
            },
        )

        harvest = self.harvester.interject_modified_code(
            capability_name=capability_name,
            source_code=generated,
            metadata={
                "derived_from": "MultiverseProcessor",
                "trust_context": trust_context.integrity_hash,
            },
        )
        return ProcessingResult(
            input_prompt=prompt,
            identity=asdict(identity),
            generated_capability=capability_name,
            harvest_result=harvest,
        )

    def _build_capability_module(self, family: str, algorithm: str) -> str:
        return f'''from __future__ import annotations

CAPABILITY_FAMILY = "{family}"
CAPABILITY_ALGORITHM = "{algorithm}"


def describe() -> dict[str, str]:
    return {{
        "family": CAPABILITY_FAMILY,
        "algorithm": CAPABILITY_ALGORITHM,
        "mode": "generated-by-multiverse-processor",
    }}
'''
