"""Policy AST and verification certificate models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PolicyRule(BaseModel):
    rule_id: str
    trigger: dict[str, Any]
    predicate: dict[str, Any]
    enforcement: dict[str, Any]
    severity: str = "medium"


class PolicyAST(BaseModel):
    policy_id: str
    name: str
    version: str = "1.0"
    description: str = ""
    imports: list[str] = Field(default_factory=list)
    rules: list[PolicyRule] = Field(default_factory=list)
    workflows: list[dict[str, Any]] = Field(default_factory=list)
    ethics_rules: list[dict[str, Any]] = Field(default_factory=list)


class VerificationCertificate(BaseModel):
    policy_hash: str
    verification_timestamp: datetime = Field(default_factory=datetime.utcnow)
    properties_proven: list[str] = Field(default_factory=list)
    verifier_version: str = "1.0"
    consistent: bool = True
    complete: bool = True
    conflicts: list[str] = Field(default_factory=list)
