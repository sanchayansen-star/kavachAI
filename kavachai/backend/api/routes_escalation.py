"""Escalation API routes — queue management and resolution."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from kavachai.backend.core.escalation import EscalationManager

router = APIRouter(prefix="/api/v1/escalations", tags=["escalations"])

# Singleton (will be replaced with DI)
escalation_mgr = EscalationManager()


class ResolveRequest(BaseModel):
    decision: str  # "approve" | "reject"
    reason: str = ""
    operator_id: str


@router.get("")
async def list_escalations(status: str = "pending", tenant_id: str = "default"):
    pending = escalation_mgr.get_pending(tenant_id)
    return [
        {
            "escalation_id": e.escalation_id,
            "action_request": e.action_request,
            "threat_score": e.threat_score,
            "kill_chain_id": e.kill_chain_id,
            "timeout_at": e.timeout_at.isoformat(),
            "status": e.status,
        }
        for e in pending
    ]


@router.post("/{escalation_id}/resolve")
async def resolve_escalation(escalation_id: str, body: ResolveRequest):
    try:
        verdict = escalation_mgr.resolve(
            escalation_id=escalation_id,
            decision=body.decision,
            operator_id=body.operator_id,
            reason=body.reason,
        )
        return {"resolved": True, "action_verdict": verdict.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
