"""Collusion detector — cross-session action graph for coordinated circumvention."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass
class CollusionAlert:
    agents: list[str]
    pattern: str
    confidence: float
    details: str


class CollusionDetector:
    """Detect coordinated policy circumvention across agents/sessions."""

    def __init__(self, time_window_minutes: int = 10) -> None:
        self._time_window = timedelta(minutes=time_window_minutes)
        # (agent_id, tool_name, timestamp)
        self._action_log: list[tuple[str, str, datetime]] = []

    def record_action(self, agent_id: str, tool_name: str, timestamp: datetime | None = None) -> None:
        self._action_log.append((agent_id, tool_name, timestamp or datetime.utcnow()))

    def detect(self) -> list[CollusionAlert]:
        alerts: list[CollusionAlert] = []
        now = datetime.utcnow()
        recent = [(a, t, ts) for a, t, ts in self._action_log if now - ts < self._time_window]

        # Pattern: multiple agents accessing same sensitive tools in short window
        tool_agents: dict[str, set[str]] = {}
        for agent_id, tool_name, _ in recent:
            tool_agents.setdefault(tool_name, set()).add(agent_id)

        for tool, agents in tool_agents.items():
            if len(agents) >= 2:
                alerts.append(CollusionAlert(
                    agents=list(agents),
                    pattern="concurrent_access",
                    confidence=min(len(agents) * 0.3, 1.0),
                    details=f"{len(agents)} agents accessed '{tool}' within {self._time_window.total_seconds() / 60:.0f}min window",
                ))

        return alerts
