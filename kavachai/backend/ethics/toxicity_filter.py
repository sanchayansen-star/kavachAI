"""Toxicity classification with configurable threshold."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ToxicityResult:
    score: float  # 0.0 - 1.0
    blocked: bool
    categories: list[str]


# Simplified keyword-based toxicity detection
_TOXICITY_KEYWORDS: dict[str, list[str]] = {
    "hate_speech": ["kill", "destroy", "eliminate", "exterminate"],
    "harassment": ["stupid", "idiot", "moron", "worthless"],
    "threat": ["bomb", "attack", "weapon", "violence"],
    "self_harm": ["suicide", "self-harm", "cut myself"],
}


class ToxicityFilter:
    """Classify text toxicity with configurable threshold."""

    def __init__(self, threshold: float = 0.7) -> None:
        self.threshold = threshold

    def classify(self, text: str) -> ToxicityResult:
        if not text:
            return ToxicityResult(score=0.0, blocked=False, categories=[])

        text_lower = text.lower()
        categories: list[str] = []
        total_matches = 0

        for category, keywords in _TOXICITY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                categories.append(category)
                total_matches += matches

        # Score based on keyword density
        words = len(text.split())
        score = min(total_matches / max(words * 0.1, 1), 1.0)

        return ToxicityResult(
            score=score,
            blocked=score >= self.threshold,
            categories=categories,
        )
