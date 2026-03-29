"""Action request, verdict, and attestation models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class VerdictType(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    FLAG = "flag"
    ESCALATE = "escalate"
    QUARANTINE = "quarantine"


class ActionRequest(BaseModel):
    request_id: str
    agent_id: str
    session_id: str
    tool_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    signature: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reasoning_trace: str | None = None
    tenant_id: str = "default"


class PolicyResult(BaseModel):
    policy_id: str
    rule_id: str
    matched: bool
    verdict: VerdictType
    reason: str


class ActionAttestation(BaseModel):
    attestation_id: str
    request_id: str
    action_hash: str  # SHA-256(tool_name + params + timestamp)
    agent_identity_hash: str
    verdict: VerdictType
    policy_results: list[PolicyResult] = Field(default_factory=list)
    threat_score: float = 0.0
    grounding_score: float | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    kavachai_signature: str = ""


class DecisionExplanation(BaseModel):
    llm_reasoning: str | None = None
    policy_evaluation: str = ""
    user_facing: str = ""


class ActionVerdict(BaseModel):
    verdict: VerdictType
    reason: str = ""
    matched_policies: list[str] = Field(default_factory=list)
    threat_score: float = 0.0
    ethics_score: float = 0.0
    grounding_score: float | None = None
    attestation: ActionAttestation | None = None
    reasoning_trace: DecisionExplanation = Field(
        default_factory=DecisionExplanation
    )
