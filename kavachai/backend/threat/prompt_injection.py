"""Prompt injection detection — pattern-based detection of embedded instructions."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class InjectionResult:
    detected: bool
    score: float  # 0.0 - 1.0
    patterns_matched: list[str]


# Patterns that indicate prompt injection attempts
_INJECTION_PATTERNS: list[tuple[str, float, re.Pattern]] = [
    ("ignore_previous", 0.9, re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I)),
    ("system_override", 0.95, re.compile(r"(system|admin)\s*(:|prompt|override|mode)", re.I)),
    ("role_switch", 0.85, re.compile(r"you\s+are\s+now\s+(a|an|the)\s+", re.I)),
    ("jailbreak_dan", 0.95, re.compile(r"\bDAN\b.*\bdo\s+anything\s+now\b", re.I)),
    ("instruction_inject", 0.8, re.compile(r"(new\s+instructions?|forget\s+everything|disregard)", re.I)),
    ("delimiter_escape", 0.7, re.compile(r"(```|<\|im_start\|>|<\|im_end\|>|\[INST\]|\[/INST\])", re.I)),
    ("base64_payload", 0.6, re.compile(r"[A-Za-z0-9+/]{40,}={0,2}")),
    ("hidden_instruction", 0.75, re.compile(r"(secretly|covertly|without\s+telling)\s+(do|execute|run|perform)", re.I)),
]


class PromptInjectionDetector:
    """Detect prompt injection attempts in tool inputs and outputs."""

    def detect(self, text: str) -> InjectionResult:
        if not text:
            return InjectionResult(detected=False, score=0.0, patterns_matched=[])

        matched: list[str] = []
        max_score = 0.0

        for name, weight, pattern in _INJECTION_PATTERNS:
            if pattern.search(text):
                matched.append(name)
                max_score = max(max_score, weight)

        return InjectionResult(
            detected=len(matched) > 0,
            score=max_score,
            patterns_matched=matched,
        )
