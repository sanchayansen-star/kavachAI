"""India-specific bias detection — gender, caste, religion, regional, socioeconomic."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class BiasResult:
    detected: bool
    score: float  # 0.0 - 1.0
    categories: list[str]


# Bias indicator patterns (simplified for demo)
_BIAS_PATTERNS: dict[str, list[re.Pattern]] = {
    "gender": [
        re.compile(r"\b(women|girls?)\s+(can't|cannot|shouldn't|are\s+not\s+capable)", re.I),
        re.compile(r"\b(men|boys?)\s+are\s+(better|superior)", re.I),
    ],
    "caste": [
        re.compile(r"\b(lower\s+caste|upper\s+caste|untouchable|dalit)\b.*\b(inferior|superior|unworthy)", re.I),
    ],
    "religion": [
        re.compile(r"\b(hindu|muslim|christian|sikh|buddhist|jain)\b.*\b(terrorist|extremist|backward)", re.I),
    ],
    "regional": [
        re.compile(r"\b(north\s+indian|south\s+indian|bihari|madrasi)\b.*\b(lazy|stupid|backward)", re.I),
    ],
    "socioeconomic": [
        re.compile(r"\b(poor|slum|low\s+income)\b.*\b(criminal|untrustworthy|lazy)", re.I),
    ],
}


class BiasDetector:
    """Detect India-specific bias patterns in text."""

    def detect(self, text: str) -> BiasResult:
        if not text:
            return BiasResult(detected=False, score=0.0, categories=[])

        categories: list[str] = []
        for category, patterns in _BIAS_PATTERNS.items():
            for pat in patterns:
                if pat.search(text):
                    categories.append(category)
                    break

        score = min(len(categories) * 0.3, 1.0) if categories else 0.0
        return BiasResult(detected=len(categories) > 0, score=score, categories=categories)
