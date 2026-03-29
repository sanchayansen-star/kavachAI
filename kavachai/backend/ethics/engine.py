"""Ethics engine — orchestrator computing Ethics_Score from four dimensions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from kavachai.backend.ethics.bias_detector import BiasDetector, BiasResult
from kavachai.backend.ethics.toxicity_filter import ToxicityFilter, ToxicityResult


@dataclass
class EthicsAssessment:
    ethics_score: float  # 0.0 - 1.0 (1.0 = fully ethical)
    bias_result: BiasResult
    toxicity_result: ToxicityResult
    blocked: bool
    reasons: list[str]


class EthicsEngine:
    """Orchestrator computing Ethics_Score from bias, toxicity, fairness, content safety."""

    def __init__(self, toxicity_threshold: float = 0.7) -> None:
        self.bias_detector = BiasDetector()
        self.toxicity_filter = ToxicityFilter(threshold=toxicity_threshold)

    def assess(self, text: str, context: dict[str, Any] | None = None) -> EthicsAssessment:
        reasons: list[str] = []
        blocked = False

        bias = self.bias_detector.detect(text)
        toxicity = self.toxicity_filter.classify(text)

        if toxicity.blocked:
            blocked = True
            reasons.append(f"Toxicity score {toxicity.score:.2f} exceeds threshold")

        if bias.detected:
            reasons.extend(f"bias:{c}" for c in bias.categories)

        # Ethics score: average of (1 - bias_score) and (1 - toxicity_score)
        ethics_score = 1.0 - max(bias.score, toxicity.score)
        ethics_score = max(0.0, min(1.0, ethics_score))

        return EthicsAssessment(
            ethics_score=ethics_score,
            bias_result=bias,
            toxicity_result=toxicity,
            blocked=blocked,
            reasons=reasons,
        )
