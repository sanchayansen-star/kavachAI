"""Multi-agent governor — delegation chain limits, privilege amplification prevention."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class DelegationRecord:
    delegator_id: str
    receiver_id: str
    task: str
    permissions: list[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GovernanceResult:
    allowed: bool
    reason: str
    chain_depth: int


class MultiAgentGovernor:
    """Enforce delegation chain depth limits and prevent privilege amplification."""

    def __init__(self, max_chain_depth: int = 3) -> None:
        self.max_chain_depth = max_chain_depth
        # agent_id -> list of delegations made
        self._delegations: dict[str, list[DelegationRecord]] = {}
        # agent_id -> set of original permissions
        self._agent_permissions: dict[str, set[str]] = {}

    def register_permissions(self, agent_id: str, permissions: list[str]) -> None:
        self._agent_permissions[agent_id] = set(permissions)

    def check_delegation(
        self,
        delegator_id: str,
        receiver_id: str,
        task: str,
        requested_permissions: list[str],
    ) -> GovernanceResult:
        # Check chain depth
        depth = self._get_chain_depth(delegator_id)
        if depth >= self.max_chain_depth:
            return GovernanceResult(
                allowed=False,
                reason=f"Delegation chain depth {depth + 1} exceeds limit {self.max_chain_depth}",
                chain_depth=depth + 1,
            )

        # Check privilege amplification
        delegator_perms = self._agent_permissions.get(delegator_id, set())
        requested = set(requested_permissions)
        amplified = requested - delegator_perms
        if amplified:
            return GovernanceResult(
                allowed=False,
                reason=f"Privilege amplification detected: {amplified}",
                chain_depth=depth + 1,
            )

        # Record delegation
        record = DelegationRecord(
            delegator_id=delegator_id,
            receiver_id=receiver_id,
            task=task,
            permissions=requested_permissions,
        )
        self._delegations.setdefault(delegator_id, []).append(record)

        return GovernanceResult(allowed=True, reason="Delegation approved", chain_depth=depth + 1)

    def _get_chain_depth(self, agent_id: str, visited: set[str] | None = None) -> int:
        if visited is None:
            visited = set()
        if agent_id in visited:
            return 0
        visited.add(agent_id)

        max_depth = 0
        for delegations in self._delegations.values():
            for d in delegations:
                if d.receiver_id == agent_id:
                    depth = 1 + self._get_chain_depth(d.delegator_id, visited)
                    max_depth = max(max_depth, depth)
        return max_depth
