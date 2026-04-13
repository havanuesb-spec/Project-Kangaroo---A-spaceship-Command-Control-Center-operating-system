from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from trust.trust_registry import TrustRegistry


@dataclass
class VoiceTimbreAssessment:
    timbre_stability: float
    resonance_match: float
    distortion_risk: float
    indicators: list[str]
    notes: list[str]


class VoiceTimbreCoherenceEngine:
    """
    This does not determine whether someone is lying.
    It estimates voice-timbre instability and mismatch signals for review.
    """

    def __init__(self, trust_registry: TrustRegistry | None = None) -> None:
        self.trust_registry = trust_registry or TrustRegistry()

    def assess(
        self,
        sample_metrics: dict[str, Any],
        reference_metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        reference_metrics = reference_metrics or {}
        indicators: list[str] = []
        notes: list[str] = []

        pitch = float(sample_metrics.get("pitch_mean", 0.0))
        jitter = float(sample_metrics.get("jitter", 0.0))
        shimmer = float(sample_metrics.get("shimmer", 0.0))
        pitch_ref = float(reference_metrics.get("pitch_mean", pitch))

        pitch_delta = abs(pitch - pitch_ref)
        timbre_stability = self._clamp(1.0 - min(jitter + shimmer, 1.0))
        resonance_match = self._clamp(1.0 - min(pitch_delta / 200.0, 1.0))
        distortion_risk = self._clamp(1.0 - ((timbre_stability * 0.55) + (resonance_match * 0.45)))

        if pitch_delta > 40:
            indicators.append("pitch drift from reference")
        if jitter > 0.12:
            indicators.append("elevated jitter")
        if shimmer > 0.12:
            indicators.append("elevated shimmer")
        if not indicators:
            indicators.append("no major timbre anomalies")
            notes.append("no major signal drift seen in provided metrics")

        assessment = VoiceTimbreAssessment(
            timbre_stability=timbre_stability,
            resonance_match=resonance_match,
            distortion_risk=distortion_risk,
            indicators=indicators,
            notes=notes,
        )
        record = self.trust_registry.issue_record(
            record_type="voice-timbre-coherence",
            source="VoiceTimbreCoherenceEngine",
            payload={"sample_metrics": sample_metrics, "reference_metrics": reference_metrics, "assessment": asdict(assessment)},
        )
        return {"assessment": asdict(assessment), "trust_record_hash": record.integrity_hash}

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, round(value, 4)))
