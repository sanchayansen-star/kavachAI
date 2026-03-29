"""Escalation manager — queue, timeout, safe defaults."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from kavachai.backend.models.action import VerdictType


class EscalationEntry:
    def __init__(
        self,
        action_request: dict[str, Any],
        threat_score: float,
        kill_chain_id: str | None = None,
        timeout_seconds: int = 60,
        tenant_id: str = "default",
    ):
        self.escalation_id = str(uuid.uuid4())
        self.action_request = action_request
        self.threat_score = threat_score
        self.kill_chain_id = kill_chain_id
        self.status = "pending"
        self.operator_id: str | None = None
        self.operator_reason: str | None = None
        self.timeout_at = datetime.utcnow() + timedelta(seconds=timeout_seconds)
        self.resolved_at: datetime | None = None
        self.tenant_id = tenant_id


class EscalationManager:
    """Manage escalation queue with configurable timeouts and safe defaults."""

    def __init__(self, default_timeout: int = 60) -> None:
        self._default_timeout = default_timeout
        self._queue: dict[str, EscalationEntry] = {}
        # Track request_ids to prevent duplicates
        self._seen_requests: set[str] = set()

    def escalate(
        self,
        action_request: dict[str, Any],
        threat_score: float,
        kill_chain_id: str | None = None,
        timeout_seconds: int | None = None,
        tenant_id: str = "default",
    ) -> EscalationEntry:
        """Add an action to the escalation queue."""
        req_id = action_request.get("request_id", "")
        if req_id in self._seen_requests:
            # Return existing entry for duplicate prevention
            for entry in self._queue.values():
                if entry.action_request.get("request_id") == req_id:
                    return entry

        entry = EscalationEntry(
            action_request=action_request,
            threat_score=threat_score,
            kill_chain_id=kill_chain_id,
            timeout_seconds=timeout_seconds or self._default_timeout,
            tenant_id=tenant_id,
        )
        self._queue[entry.escalation_id] = entry
        if req_id:
            self._seen_requests.add(req_id)
        return entry

    def resolve(
        self,
        escalation_id: str,
        decision: str,  # "approve" | "reject"
        operator_id: str,
        reason: str = "",
    ) -> VerdictType:
        """Resolve an escalation. Returns the resulting verdict."""
        entry = self._queue.get(escalation_id)
        if not entry:
            raise ValueError(f"Escalation {escalation_id} not found")

        entry.status = "approved" if decision == "approve" else "rejected"
        entry.operator_id = operator_id
        entry.operator_reason = reason
        entry.resolved_at = datetime.utcnow()

        return VerdictType.ALLOW if decision == "approve" else VerdictType.BLOCK

    def check_timeouts(self) -> list[EscalationEntry]:
        """Check for timed-out escalations and apply safe default (BLOCK)."""
        now = datetime.utcnow()
        timed_out = []
        for entry in self._queue.values():
            if entry.status == "pending" and now >= entry.timeout_at:
                entry.status = "timeout"
                entry.resolved_at = now
                timed_out.append(entry)
        return timed_out

    def get_pending(self, tenant_id: str | None = None) -> list[EscalationEntry]:
        """Get pending escalations sorted by threat score (highest first)."""
        pending = [
            e for e in self._queue.values()
            if e.status == "pending" and (tenant_id is None or e.tenant_id == tenant_id)
        ]
        return sorted(pending, key=lambda e: e.threat_score, reverse=True)
