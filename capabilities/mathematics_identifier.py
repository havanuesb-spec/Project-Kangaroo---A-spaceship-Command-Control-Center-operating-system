from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class MathIdentity:
    family: str
    algorithm: str
    confidence: float
    evidence: list[str]


class MathematicsAlgorithmIdentifier:
    def identify(self, prompt: str) -> MathIdentity:
        text = prompt.lower()
        evidence: list[str] = []

        def seen(pattern: str, label: str) -> bool:
            if re.search(pattern, text):
                evidence.append(label)
                return True
            return False

        if seen(r"\b(matrix|vector|determinant|eigen|rank)\b", "matrix vocabulary"):
            return MathIdentity("linear-algebra", "matrix-operator", 0.93, evidence)
        if seen(r"\b(derivative|integral|differentiate|integrate|limit)\b", "calculus vocabulary"):
            return MathIdentity("calculus", "symbolic-calculus", 0.93, evidence)
        if seen(r"\b(probability|distribution|variance|mean|median|regression)\b", "statistics vocabulary"):
            return MathIdentity("statistics", "statistical-analysis", 0.9, evidence)
        if seen(r"\b(prime|mod|divisible|gcd|lcm|factor)\b", "number theory vocabulary"):
            return MathIdentity("number-theory", "modular-number-theory", 0.89, evidence)
        if seen(r"\b(sequence|series|fibonacci|recurrence|sum)\b", "sequence vocabulary"):
            return MathIdentity("discrete-math", "sequence-evaluator", 0.86, evidence)
        if seen(r"\b(angle|triangle|circle|polygon|radius|area|volume)\b", "geometry vocabulary"):
            return MathIdentity("geometry", "geometric-solver", 0.86, evidence)
        if seen(r"\b(and|or|not|implies|truth table|boolean)\b", "logic vocabulary"):
            return MathIdentity("logic", "propositional-logic", 0.83, evidence)
        if seen(r"\b(system of equations|simultaneous|solve for)\b", "equation-system vocabulary"):
            return MathIdentity("algebra", "equation-system-solver", 0.88, evidence)
        if re.search(r"[=+\-*/^]", text):
            evidence.append("generic operators")
            return MathIdentity("arithmetic-algebra", "expression-evaluator", 0.72, evidence)

        evidence.append("no strong pattern match")
        return MathIdentity("unknown", "human-review-needed", 0.35, evidence)
