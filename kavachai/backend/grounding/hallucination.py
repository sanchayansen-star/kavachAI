"""Hallucination detector — compare agent claims against attestation records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class HallucinationType(str, Enum):
    TOOL_FABRICATION = "tool_fabrication"  # No attestation exists
    RESULT_MISSTATEMENT = "result_misstatement"  # Values differ from attestation
    UNGROUNDED = "ungrounded"  # Claim not backed by any source


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class HallucinationFinding:
    hallucination_type: HallucinationType
    claim: str
    severity: Severity
    details: str


@dataclass
class HallucinationResult:
    findings: list[HallucinationFinding]
    should_block: bool
    should_escalate: bool


class HallucinationDetector:
    """Detect hallucinations by comparing agent claims against attestation records."""

    def detect(
        self,
        agent_output: str,
        attestations: list[dict[str, Any]],
        grounded_claims: list[dict[str, Any]] | None = None,
    ) -> HallucinationResult:
        findings: list[HallucinationFinding] = []

        # Extract tool-related claims from output
        tool_claims = self._extract_tool_claims(agent_output)
        attested_tools = {a.get("tool_name") for a in attestations}
        attested_results = {a.get("tool_name"): a.get("result") for a in attestations}

        for claim in tool_claims:
            tool_name = claim.get("tool_name", "")

            # TOOL_FABRICATION: agent claims to have called a tool with no attestation
            if tool_name and tool_name not in attested_tools:
                findings.append(HallucinationFinding(
                    hallucination_type=HallucinationType.TOOL_FABRICATION,
                    claim=f"Claimed tool call: {tool_name}",
                    severity=Severity.HIGH,
                    details=f"No attestation found for tool '{tool_name}'",
                ))

            # RESULT_MISSTATEMENT: agent states values that differ from actual tool response
            elif tool_name in attested_results:
                actual = attested_results[tool_name]
                claimed_value = claim.get("value")
                if claimed_value and actual and str(claimed_value) != str(actual):
                    findings.append(HallucinationFinding(
                        hallucination_type=HallucinationType.RESULT_MISSTATEMENT,
                        claim=f"Claimed result for {tool_name}: {claimed_value}",
                        severity=Severity.MEDIUM,
                        details=f"Actual result: {actual}",
                    ))

        # UNGROUNDED: claims not backed by any source
        if grounded_claims:
            for gc in grounded_claims:
                if not gc.get("grounded", False):
                    findings.append(HallucinationFinding(
                        hallucination_type=HallucinationType.UNGROUNDED,
                        claim=gc.get("claim_text", ""),
                        severity=Severity.LOW,
                        details="Claim not backed by knowledge graph, ontology, or tool response",
                    ))

        should_block = any(f.severity == Severity.HIGH for f in findings)
        should_escalate = should_block or len(findings) >= 3

        return HallucinationResult(
            findings=findings,
            should_block=should_block,
            should_escalate=should_escalate,
        )

    @staticmethod
    def _extract_tool_claims(text: str) -> list[dict[str, Any]]:
        """Extract claims about tool calls from agent output text."""
        import re
        claims: list[dict[str, Any]] = []
        # Pattern: "I called/used/ran <tool_name>" or "<tool_name> returned <value>"
        patterns = [
            re.compile(r"(?:called|used|ran|executed)\s+(\w+)", re.I),
            re.compile(r"(\w+)\s+(?:returned|showed|gave|reported)\s+(.+?)(?:\.|$)", re.I),
        ]
        for pat in patterns:
            for m in pat.finditer(text):
                claim: dict[str, Any] = {"tool_name": m.group(1)}
                if m.lastindex and m.lastindex >= 2:
                    claim["value"] = m.group(2).strip()
                claims.append(claim)
        return claims
