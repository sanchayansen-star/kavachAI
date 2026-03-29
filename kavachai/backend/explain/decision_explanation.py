"""3-layer decision explanation generator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ThreeLayerExplanation:
    llm_reasoning: str | None  # Raw chain-of-thought
    policy_evaluation: str  # Technical policy trace
    user_facing: str  # Human-readable summary


class DecisionExplainer:
    """Generate 3-layer explanations for safety decisions."""

    def explain(
        self,
        verdict: str,
        matched_rules: list[str],
        threat_score: float,
        ethics_score: float,
        llm_reasoning: str | None = None,
        language: str = "en",
    ) -> ThreeLayerExplanation:
        # Layer 1: LLM reasoning (pass-through)
        # Layer 2: Policy evaluation trace
        policy_trace = self._build_policy_trace(verdict, matched_rules, threat_score, ethics_score)
        # Layer 3: User-facing summary
        user_summary = self._build_user_summary(verdict, matched_rules, threat_score, language)

        return ThreeLayerExplanation(
            llm_reasoning=llm_reasoning,
            policy_evaluation=policy_trace,
            user_facing=user_summary,
        )

    @staticmethod
    def _build_policy_trace(verdict: str, rules: list[str], threat: float, ethics: float) -> str:
        parts = [f"Verdict: {verdict.upper()}"]
        if rules:
            parts.append(f"Matched rules: {', '.join(rules)}")
        parts.append(f"Threat score: {threat:.2f}")
        parts.append(f"Ethics score: {ethics:.2f}")
        return " | ".join(parts)

    @staticmethod
    def _build_user_summary(verdict: str, rules: list[str], threat: float, language: str) -> str:
        if language == "hi":
            return _hindi_summary(verdict, rules, threat)
        return _english_summary(verdict, rules, threat)


def _english_summary(verdict: str, rules: list[str], threat: float) -> str:
    if verdict == "allow":
        return "This action was permitted after passing all safety checks."
    if verdict == "block":
        return f"This action was blocked. Reason: safety policy violation ({', '.join(rules) if rules else 'threat detected'})."
    if verdict == "escalate":
        return "This action requires human review before proceeding."
    if verdict == "quarantine":
        return "This action was quarantined due to critical safety concerns. The session has been suspended."
    if verdict == "flag":
        return "This action was permitted with a warning. It has been flagged for review."
    return f"Action result: {verdict}"


def _hindi_summary(verdict: str, rules: list[str], threat: float) -> str:
    if verdict == "allow":
        return "यह कार्रवाई सभी सुरक्षा जांचों को पास करने के बाद अनुमत की गई।"
    if verdict == "block":
        return "यह कार्रवाई अवरुद्ध कर दी गई। कारण: सुरक्षा नीति उल्लंघन।"
    if verdict == "escalate":
        return "इस कार्रवाई के लिए आगे बढ़ने से पहले मानव समीक्षा आवश्यक है।"
    if verdict == "quarantine":
        return "गंभीर सुरक्षा चिंताओं के कारण इस कार्रवाई को क्वारंटाइन किया गया।"
    return f"कार्रवाई परिणाम: {verdict}"
