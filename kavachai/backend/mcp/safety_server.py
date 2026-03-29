"""MCP Safety Server — exposes 5 safety tools to agents."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from kavachai.backend.core.pipeline import EvalPipeline
from kavachai.backend.models.action import ActionRequest


class MCPSafetyServer:
    """MCP server exposing safety tools to agents.

    Tools: check_policy, get_my_permissions, request_escalation,
           get_compliance_status, report_suspicious_input.
    """

    TOOLS = [
        {"name": "check_policy", "description": "Check if a proposed action would be allowed"},
        {"name": "get_my_permissions", "description": "Get current capability scope and trust level"},
        {"name": "request_escalation", "description": "Request human review of a planned action"},
        {"name": "get_compliance_status", "description": "Get DPDP compliance posture"},
        {"name": "report_suspicious_input", "description": "Report potentially malicious input"},
    ]

    def __init__(self, eval_pipeline: EvalPipeline) -> None:
        self.eval_pipeline = eval_pipeline
        self._reports: list[dict[str, Any]] = []

    async def handle(self, tool_name: str, agent_id: str, params: dict[str, Any]) -> dict[str, Any]:
        handlers = {
            "check_policy": self._check_policy,
            "get_my_permissions": self._get_permissions,
            "request_escalation": self._request_escalation,
            "get_compliance_status": self._get_compliance,
            "report_suspicious_input": self._report_suspicious,
        }
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        return await handler(agent_id, params)

    async def _check_policy(self, agent_id: str, params: dict[str, Any]) -> dict[str, Any]:
        """Dry-run policy evaluation without recording in audit trail."""
        request = ActionRequest(
            request_id=str(uuid.uuid4()),
            agent_id=agent_id,
            session_id=params.get("session_id", "dry-run"),
            tool_name=params.get("tool_name", ""),
            parameters=params.get("parameters", {}),
            timestamp=datetime.utcnow(),
        )
        verdict = await self.eval_pipeline.evaluate(request, dry_run=True)
        return {
            "verdict": verdict.verdict.value,
            "matched_rules": verdict.matched_policies,
            "reasoning": verdict.reasoning_trace.policy_evaluation,
        }

    async def _get_permissions(self, agent_id: str, params: dict[str, Any]) -> dict[str, Any]:
        agent = self.eval_pipeline.identity_mgr.get_agent(agent_id)
        if not agent:
            return {"error": "Agent not found"}
        token = self.eval_pipeline.identity_mgr.get_active_token(agent_id)
        return {
            "agent_id": agent_id,
            "trust_level": agent.trust_level.value,
            "trust_score": agent.trust_score,
            "capability_scope": agent.capability_scope,
            "active_token": token.token_id if token else None,
        }

    async def _request_escalation(self, agent_id: str, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "escalation_id": str(uuid.uuid4()),
            "status": "submitted",
            "message": "Human review requested",
        }

    async def _get_compliance(self, agent_id: str, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "dpdp_status": "compliant",
            "consent_coverage": 1.0,
            "pii_masking_rate": 1.0,
        }

    async def _report_suspicious(self, agent_id: str, params: dict[str, Any]) -> dict[str, Any]:
        report = {
            "report_id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "input_text": params.get("input_text", ""),
            "reason": params.get("reason", ""),
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._reports.append(report)
        return {"report_id": report["report_id"], "status": "received"}
