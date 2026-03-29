"""Audit trail, evidence package, and provenance models."""

from datetime import datetime

from pydantic import BaseModel, Field

from .action import VerdictType


class ModelProvenanceRecord(BaseModel):
    model_name: str
    model_version: str
    provider: str
    temperature: float = 0.0
    token_count_input: int = 0
    token_count_output: int = 0
    latency_ms: float = 0.0


class AuditEntry(BaseModel):
    entry_id: int
    timestamp: datetime
    session_id: str
    tenant_id: str = "default"
    agent_identity_hash: str
    action_type: str
    action_parameters_hash: str
    action_verdict: VerdictType
    matched_policies: list[str] = Field(default_factory=list)
    threat_score: float = 0.0
    ethics_score: float = 0.0
    grounding_score: float | None = None
    llm_reasoning: str | None = None
    model_provenance: ModelProvenanceRecord | None = None
    llm_cost: float | None = None
    trust_score_before: float = 0.5
    trust_score_after: float = 0.5
    previous_entry_hash: str = ""
    entry_hash: str = ""
    sequence_number: int = 0


class ChainOfCustodyEntry(BaseModel):
    component: str
    component_hash: str
    timestamp: datetime
    action: str


class EvidencePackage(BaseModel):
    package_id: str
    session_id: str
    entries: list[AuditEntry]
    hash_chain_valid: bool
    chain_of_custody: list[ChainOfCustodyEntry] = Field(default_factory=list)
    digital_signature: str = ""
    generated_at: datetime = Field(default_factory=datetime.utcnow)
