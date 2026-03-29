"""Semantic grounding, claim verification, and source attribution models."""

from pydantic import BaseModel, Field


class SourceAttribution(BaseModel):
    source_type: str  # knowledge_graph | document | tool_response | ontology
    source_id: str
    source_label: str
    evidence_text: str
    confidence: float = 1.0


class ClaimVerification(BaseModel):
    claim_text: str
    source_attribution: SourceAttribution | None = None
    grounded: bool = False
    confidence: float = 0.0


class ValidationCheck(BaseModel):
    check_type: str  # numerical_consistency | date_validity | entity_existence | regulatory | cross_reference
    passed: bool
    details: str


class GroundingResult(BaseModel):
    output_id: str
    session_id: str
    grounding_score: float = 0.0
    claims: list[ClaimVerification] = Field(default_factory=list)
    schema_valid: bool = True
    deterministic_checks: list[ValidationCheck] = Field(default_factory=list)
    verdict: str = "GROUNDED"
