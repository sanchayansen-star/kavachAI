"""Privilege escalation detection — scope creep analysis across action sequences."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EscalationResult:
    detected: bool
    score: float
    indicators: list[str]


# Tools considered high-privilege
_HIGH_PRIV_TOOLS = {"admin_panel", "admin_access", "sudo", "root", "system_config", "delete_user", "grant_role"}
_SENSITIVE_TOOLS = {"payment_process", "transfer_funds", "modify_account", "export_data"}


class PrivilegeEscalationDetector:
    """Detect privilege escalation attempts via scope creep analysis."""

    def __init__(self) -> None:
        # session_id -> set of tools called
        self._session_tools: dict[str, list[str]] = {}

    def detect(
        self,
        session_id: str,
        tool_name: str,
        agent_scope: list[str] | None = None,
    ) -> EscalationResult:
        history = self._session_tools.setdefault(session_id, [])
        history.append(tool_name)
        indicators: list[str] = []
        score = 0.0

        # Direct high-privilege tool access
        if tool_name.lower() in _HIGH_PRIV_TOOLS or tool_name.startswith("admin_"):
            indicators.append(f"high_privilege_tool: {tool_name}")
            score = max(score, 0.8)

        # Out-of-scope tool call
        if agent_scope and tool_name not in agent_scope:
            indicators.append(f"out_of_scope: {tool_name}")
            score = max(score, 0.7)

        # Rapid escalation pattern: normal tools → sensitive → admin
        if len(history) >= 3:
            recent = history[-3:]
            has_sensitive = any(t in _SENSITIVE_TOOLS for t in recent)
            has_admin = any(t in _HIGH_PRIV_TOOLS or t.startswith("admin_") for t in recent)
            if has_sensitive and has_admin:
                indicators.append("rapid_escalation_pattern")
                score = max(score, 0.9)

        return EscalationResult(detected=len(indicators) > 0, score=score, indicators=indicators)
