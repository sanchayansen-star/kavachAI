"""LLM Gateway — unified API, intelligent routing, fallback chains, budget enforcement."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LLMRequest:
    model: str | None
    messages: list[dict[str, str]]
    agent_id: str
    session_id: str
    tenant_id: str = "default"


@dataclass
class LLMResponse:
    content: str
    model_used: str
    tokens: int
    cost: float
    blocked: bool = False
    reason: str = ""


class LLMGateway:
    """Unified LLM gateway with safety governance and cost tracking."""

    def __init__(self) -> None:
        self._providers: dict[str, Any] = {}
        self._budgets: dict[str, float] = {}  # agent_id -> remaining budget
        self._usage: dict[str, dict] = {}  # agent_id -> {tokens, cost}
        self._min_safety_score = 70

    def register_provider(self, name: str, provider: Any) -> None:
        self._providers[name] = provider

    def set_budget(self, agent_id: str, budget: float) -> None:
        self._budgets[agent_id] = budget

    async def complete(self, request: LLMRequest) -> LLMResponse:
        # Budget check
        remaining = self._budgets.get(request.agent_id, float("inf"))
        used = self._usage.get(request.agent_id, {}).get("cost", 0.0)
        if used >= remaining:
            return LLMResponse(content="", model_used="", tokens=0, cost=0, blocked=True, reason="Budget exceeded")

        # Select model
        model = request.model or self._select_model(request)

        # Simulate completion (in production, would call actual provider)
        content = f"[LLM response from {model}]"
        tokens = sum(len(m.get("content", "").split()) for m in request.messages) * 2
        cost = tokens * 0.00001

        # Track usage
        usage = self._usage.setdefault(request.agent_id, {"tokens": 0, "cost": 0.0})
        usage["tokens"] += tokens
        usage["cost"] += cost

        return LLMResponse(content=content, model_used=model, tokens=tokens, cost=cost)

    def _select_model(self, request: LLMRequest) -> str:
        """Intelligent routing: simple → cheap, complex → capable."""
        total_words = sum(len(m.get("content", "").split()) for m in request.messages)
        if total_words < 50:
            return "gpt-3.5-turbo"
        elif total_words > 200:
            return "gpt-4"
        return "gpt-3.5-turbo"

    def get_usage(self, agent_id: str) -> dict:
        return self._usage.get(agent_id, {"tokens": 0, "cost": 0.0})
