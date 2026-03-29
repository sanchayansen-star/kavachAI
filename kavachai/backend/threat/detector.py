"""Threat detector orchestrator — aggregates sub-detector results."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from kavachai.backend.models.action import ActionRequest
from kavachai.backend.threat.attack_chain import AttackChainAnalyzer, ChainAnalysis
from kavachai.backend.threat.covert_channel import CovertChannelDetector
from kavachai.backend.threat.privilege_escalation import PrivilegeEscalationDetector
from kavachai.backend.threat.prompt_injection import PromptInjectionDetector
from kavachai.backend.threat.tool_poisoning import ToolPoisoningDetector


@dataclass
class ThreatAssessment:
    session_threat_score: float  # 0.0 - 1.0
    sub_scores: dict[str, float]
    indicators: list[str]
    chain_analysis: ChainAnalysis | None


class ThreatDetector:
    """Orchestrator that runs all sub-detectors and aggregates results.

    Target: each action evaluated within 50ms.
    """

    def __init__(self) -> None:
        self.prompt_injection = PromptInjectionDetector()
        self.tool_poisoning = ToolPoisoningDetector()
        self.privilege_escalation = PrivilegeEscalationDetector()
        self.covert_channel = CovertChannelDetector()
        self.attack_chain = AttackChainAnalyzer()

    def assess(
        self,
        request: ActionRequest,
        agent_scope: list[str] | None = None,
        tool_response: Any = None,
    ) -> ThreatAssessment:
        sub_scores: dict[str, float] = {}
        indicators: list[str] = []

        # 1. Prompt injection in parameters
        param_text = " ".join(str(v) for v in request.parameters.values())
        inj = self.prompt_injection.detect(param_text)
        sub_scores["prompt_injection"] = inj.score
        if inj.detected:
            indicators.extend(f"injection:{p}" for p in inj.patterns_matched)

        # 2. Tool poisoning (if response available)
        if tool_response is not None:
            poison = self.tool_poisoning.detect(request.tool_name, tool_response)
            sub_scores["tool_poisoning"] = poison.score
            if poison.detected:
                indicators.extend(f"poisoning:{d}" for d in poison.deviations)

        # 3. Privilege escalation
        esc = self.privilege_escalation.detect(
            request.session_id, request.tool_name, agent_scope
        )
        sub_scores["privilege_escalation"] = esc.score
        if esc.detected:
            indicators.extend(f"escalation:{i}" for i in esc.indicators)

        # 4. Covert channel in parameters
        cov = self.covert_channel.detect(param_text)
        sub_scores["covert_channel"] = cov.score
        if cov.detected:
            indicators.extend(f"covert:{i}" for i in cov.indicators)

        # 5. Attack chain analysis
        chain = self.attack_chain.analyze(
            session_id=request.session_id,
            tool_name=request.tool_name,
            params=request.parameters,
            threat_scores=sub_scores,
            timestamp=request.timestamp,
        )

        # Weighted session-level score — recent actions contribute more
        session_score = self._aggregate_score(sub_scores, chain.threat_score)

        return ThreatAssessment(
            session_threat_score=session_score,
            sub_scores=sub_scores,
            indicators=indicators,
            chain_analysis=chain,
        )

    @staticmethod
    def _aggregate_score(sub_scores: dict[str, float], chain_score: float) -> float:
        """Weighted aggregation — max of sub-scores blended with chain score."""
        if not sub_scores:
            return chain_score
        max_sub = max(sub_scores.values())
        # Blend: 60% max sub-detector, 40% chain analysis
        blended = 0.6 * max_sub + 0.4 * chain_score
        return min(max(blended, 0.0), 1.0)
