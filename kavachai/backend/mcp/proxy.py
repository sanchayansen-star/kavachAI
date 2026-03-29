"""MCP Proxy Gateway — transparent proxy between MCP clients and servers."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from kavachai.backend.core.pipeline import EvalPipeline
from kavachai.backend.models.action import ActionRequest, VerdictType


class MCPError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class MCPProxyGateway:
    """Transparent proxy between MCP clients and MCP servers.

    Intercepts tool calls, runs them through the evaluation pipeline,
    and forwards or blocks based on the verdict.
    """

    def __init__(self, eval_pipeline: EvalPipeline) -> None:
        self.eval_pipeline = eval_pipeline
        # server_id -> connection info
        self.downstream_servers: dict[str, dict[str, Any]] = {}
        # tool_name -> server_id
        self.tool_routing: dict[str, str] = {}
        # client_id -> session_id
        self._sessions: dict[str, str] = {}
        # Simulated downstream tool results
        self._tool_results: dict[str, Any] = {}

    def register_server(self, server_id: str, tools: list[dict[str, Any]]) -> None:
        """Register a downstream MCP server and its tools."""
        self.downstream_servers[server_id] = {"tools": tools}
        for tool in tools:
            self.tool_routing[tool["name"]] = server_id

    def get_session(self, client_id: str) -> str:
        if client_id not in self._sessions:
            self._sessions[client_id] = str(uuid.uuid4())
        return self._sessions[client_id]

    async def handle_tools_list(
        self, client_id: str, agent_id: str, allowed_tools: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Aggregate tools from downstream servers, filter by capability token."""
        all_tools: list[dict[str, Any]] = []
        for server_id, info in self.downstream_servers.items():
            all_tools.extend(info["tools"])

        if allowed_tools:
            all_tools = [t for t in all_tools if t["name"] in allowed_tools]

        # Attach capability labels
        for tool in all_tools:
            tool["metadata"] = tool.get("metadata", {})
            tool["metadata"]["capability_label"] = f"kavachai:{tool['name']}"

        return all_tools

    async def handle_tools_call(
        self,
        client_id: str,
        agent_id: str,
        tool_name: str,
        arguments: dict[str, Any],
        tenant_id: str = "default",
    ) -> dict[str, Any]:
        """Intercept tool call, run eval pipeline, forward on ALLOW."""
        session_id = self.get_session(client_id)

        action_request = ActionRequest(
            request_id=str(uuid.uuid4()),
            agent_id=agent_id,
            session_id=session_id,
            tool_name=tool_name,
            parameters=arguments,
            timestamp=datetime.utcnow(),
            tenant_id=tenant_id,
        )

        verdict = await self.eval_pipeline.evaluate(action_request)

        if verdict.verdict == VerdictType.ALLOW:
            # Forward to downstream server
            result = self._tool_results.get(tool_name, {"status": "ok"})
            return {"result": result, "verdict": "allow"}

        if verdict.verdict == VerdictType.BLOCK:
            raise MCPError(code=-32600, message=f"Blocked: {verdict.reason}")

        if verdict.verdict == VerdictType.ESCALATE:
            raise MCPError(code=-32600, message=f"Escalated: {verdict.reason}")

        if verdict.verdict == VerdictType.QUARANTINE:
            raise MCPError(code=-32600, message=f"Quarantined: {verdict.reason}")

        raise MCPError(code=-32600, message=f"Unexpected verdict: {verdict.verdict}")
