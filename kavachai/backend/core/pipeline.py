"""Zero Trust 10-stage evaluation pipeline."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from typing import Any

from kavachai.backend.audit.hash_chain import compute_identity_hash
from kavachai.backend.audit.trail import CryptographicAuditTrail
from kavachai.backend.core.identity import AgentIdentityManager
from kavachai.backend.core.policy_engine import PolicyEngine, PolicyMatch
from kavachai.backend.models.action import (
    ActionAttestation,
    ActionRequest,
    ActionVerdict,
    DecisionExplanation,
    PolicyResult,
    VerdictType,
)
from kavachai.backend.threat.detector import ThreatDetector

# Verdicts that short-circuit the pipeline
_HALT_VERDICTS = {VerdictType.BLOCK, VerdictType.ESCALATE, VerdictType.QUARANTINE}


class EvalPipeline:
    """10-stage Zero Trust evaluation pipeline.

    Stages: auth → cap_token → dsl_policy → threat → dpdp → ethics →
            pii_mask → reasoning → grounding → attestation

    Short-circuit: BLOCK/ESCALATE/QUARANTINE halts immediately.
    FLAG: permit action, record warning.
    Target: <100ms total latency.
    """

    def __init__(
        self,
        identity_mgr: AgentIdentityManager | None = None,
        policy_engine: PolicyEngine | None = None,
        threat_detector: ThreatDetector | None = None,
    ) -> None:
        self.identity_mgr = identity_mgr or AgentIdentityManager()
        self.policy_engine = policy_engine or PolicyEngine()
        self.threat_detector = threat_detector or ThreatDetector()
        self.audit_trail = CryptographicAuditTrail()

    async def evaluate(
        self,
        request: ActionRequest,
        dry_run: bool = False,
    ) -> ActionVerdict:
        """Run the full evaluation pipeline on an ActionRequest."""
        ctx: dict[str, Any] = {}
        matched_policies: list[str] = []
        threat_score = 0.0
        ethics_score = 1.0
        grounding_score: float | None = None
        reasons: list[str] = []

        # ── Stage 1: Authentication ──
        agent = self.identity_mgr.get_agent(request.agent_id)
        if not agent:
            return self._make_verdict(VerdictType.BLOCK, "Unknown agent", request=request)
        if agent.revoked:
            return self._make_verdict(VerdictType.BLOCK, "Agent revoked", request=request)
        ctx["agent"] = {
            "trust_level": agent.trust_level.value,
            "trust_score": agent.trust_score,
            "capability_scope": agent.capability_scope,
        }

        # ── Stage 2: Capability Token ──
        token = self.identity_mgr.get_active_token(request.agent_id)
        if not token:
            return self._make_verdict(VerdictType.BLOCK, "No active capability token", request=request)
        allowed_tools = [t.tool_name for t in token.allowed_tools]
        if not self._tool_in_scope(request.tool_name, allowed_tools):
            return self._make_verdict(
                VerdictType.BLOCK,
                f"Tool '{request.tool_name}' not in capability scope",
                request=request,
            )

        # ── Stage 3: DSL Policy Evaluation ──
        policy_matches = self.policy_engine.evaluate(request, ctx)
        for pm in policy_matches:
            matched_policies.append(pm.rule_id)
            if pm.verdict in _HALT_VERDICTS:
                return self._make_verdict(
                    pm.verdict,
                    pm.reason,
                    matched_policies=matched_policies,
                    request=request,
                )
            if pm.verdict == VerdictType.FLAG:
                reasons.append(f"FLAG: {pm.reason}")

        # ── Stage 4: Threat Detection ──
        assessment = self.threat_detector.assess(request, agent_scope=agent.capability_scope)
        threat_score = assessment.session_threat_score
        if threat_score >= 0.8:
            return self._make_verdict(
                VerdictType.QUARANTINE,
                f"High threat score: {threat_score:.2f}",
                threat_score=threat_score,
                matched_policies=matched_policies,
                request=request,
            )
        if threat_score >= 0.6:
            return self._make_verdict(
                VerdictType.ESCALATE,
                f"Elevated threat score: {threat_score:.2f}",
                threat_score=threat_score,
                matched_policies=matched_policies,
                request=request,
            )

        # ── Stage 5: DPDP Compliance (placeholder) ──
        # Will be implemented in Task 9

        # ── Stage 6: Ethics (placeholder) ──
        # Will be implemented in Task 19

        # ── Stage 7: PII Masking (placeholder) ──
        # Will be implemented in Task 9

        # ── Stage 8: LLM Reasoning Capture (placeholder) ──
        # Will be implemented in Task 20

        # ── Stage 9: Semantic Grounding (placeholder) ──
        # Will be implemented in Task 21

        # ── Stage 10: Attestation ──
        attestation = self._create_attestation(request, policy_matches, threat_score, grounding_score)

        # Record audit entry (unless dry run)
        if not dry_run:
            agent_hash = compute_identity_hash(agent.agent_id, agent.public_key)
            await self.audit_trail.append(
                session_id=request.session_id,
                tenant_id=request.tenant_id,
                agent_identity_hash=agent_hash,
                action_type=request.tool_name,
                parameters=request.parameters,
                verdict=VerdictType.ALLOW,
                matched_policies=matched_policies,
                threat_score=threat_score,
                ethics_score=ethics_score,
                grounding_score=grounding_score,
                trust_score_before=agent.trust_score,
                trust_score_after=agent.trust_score,
            )

        return ActionVerdict(
            verdict=VerdictType.ALLOW,
            reason="; ".join(reasons) if reasons else "All checks passed",
            matched_policies=matched_policies,
            threat_score=threat_score,
            ethics_score=ethics_score,
            grounding_score=grounding_score,
            attestation=attestation,
            reasoning_trace=DecisionExplanation(
                policy_evaluation=f"Evaluated {len(policy_matches)} rules",
                user_facing="Action permitted after safety evaluation",
            ),
        )

    @staticmethod
    def _tool_in_scope(tool_name: str, allowed: list[str]) -> bool:
        import fnmatch
        for pat in allowed:
            if pat == "*" or fnmatch.fnmatch(tool_name, pat):
                return True
        return False

    @staticmethod
    def _create_attestation(
        request: ActionRequest,
        matches: list[PolicyMatch],
        threat_score: float,
        grounding_score: float | None,
    ) -> ActionAttestation:
        action_hash = hashlib.sha256(
            f"{request.tool_name}:{json.dumps(request.parameters, sort_keys=True)}:{request.timestamp.isoformat()}".encode()
        ).hexdigest()

        return ActionAttestation(
            attestation_id=str(uuid.uuid4()),
            request_id=request.request_id,
            action_hash=action_hash,
            agent_identity_hash=request.agent_id,
            verdict=VerdictType.ALLOW,
            policy_results=[
                PolicyResult(
                    policy_id="",
                    rule_id=m.rule_id,
                    matched=m.matched,
                    verdict=m.verdict,
                    reason=m.reason,
                )
                for m in matches
            ],
            threat_score=threat_score,
            grounding_score=grounding_score,
        )

    @staticmethod
    def _make_verdict(
        verdict: VerdictType,
        reason: str,
        threat_score: float = 0.0,
        matched_policies: list[str] | None = None,
        request: ActionRequest | None = None,
    ) -> ActionVerdict:
        return ActionVerdict(
            verdict=verdict,
            reason=reason,
            matched_policies=matched_policies or [],
            threat_score=threat_score,
            reasoning_trace=DecisionExplanation(
                policy_evaluation=reason,
                user_facing=f"Action {verdict.value}: {reason}",
            ),
        )
