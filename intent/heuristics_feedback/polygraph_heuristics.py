from __future__ import annotations

from intent.heuristics_feedback.models import HeuristicAssessment, HeuristicSignal


class CoherenceHeuristics:
    """
    This is not a truth detector.
    It scores coherence, distortion, and reconstruction signals so the system
    can flag unstable statements for review inside a photonic-style model.
    """

    def assess(self, signal: HeuristicSignal) -> HeuristicAssessment:
        text = signal.statement.lower()
        indicators: list[str] = []
        notes: list[str] = []

        consistency = 0.85
        evidence = 0.55
        distortion = 0.15

        for prior in signal.prior_statements:
            prior_text = prior.lower()
            if prior_text and prior_text != text and self._shares_subject_overlap(prior_text, text):
                indicators.append("subject overlap with changed wording")
                consistency -= 0.12

        if any(term in text for term in ["always", "never", "guaranteed", "impossible"]):
            indicators.append("absolute language")
            notes.append("absolute claims often need stronger corroboration")
            evidence -= 0.08
            distortion += 0.05

        if any(term in text for term in ["honestly", "trust me", "believe me", "to be truthful"]):
            indicators.append("signal-amplification language")
            notes.append("self-attestation language can indicate persuasion pressure")
            distortion += 0.12

        if len(text.split()) < 4:
            indicators.append("very low detail")
            evidence -= 0.1

        if signal.observed_behavior.get("tamper_events", 0) > 0:
            indicators.append("coherence tamper events present")
            distortion += 0.25
            consistency -= 0.08

        if signal.context.get("has_supporting_artifacts"):
            indicators.append("supporting artifacts present")
            evidence += 0.2
        else:
            notes.append("no supporting artifacts in context")

        consistency = self._clamp(consistency)
        evidence = self._clamp(evidence)
        distortion = self._clamp(distortion)
        distortion_risk = self._clamp((1 - consistency) * 0.45 + (1 - evidence) * 0.3 + distortion * 0.6)
        reconstruction_confidence = self._clamp(1 - distortion_risk)

        if not indicators:
            indicators.append("no major coherence flags")

        return HeuristicAssessment(
            consistency_score=consistency,
            evidence_score=evidence,
            distortion_risk=distortion_risk,
            reconstruction_confidence=reconstruction_confidence,
            indicators=indicators,
            notes=notes,
        )

    def _shares_subject_overlap(self, left: str, right: str) -> bool:
        left_tokens = {token for token in left.split() if len(token) > 3}
        right_tokens = {token for token in right.split() if len(token) > 3}
        return len(left_tokens.intersection(right_tokens)) >= 2

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, round(value, 4)))


# Compatibility alias while the codebase shifts to photonic/coherence language.
PolygraphHeuristics = CoherenceHeuristics
