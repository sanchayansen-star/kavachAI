"""Agent identity, capability tokens, and trust level models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TrustLevel(str, Enum):
    TRUSTED = "trusted"          # 0.8 - 1.0
    STANDARD = "standard"        # 0.5 - 0.79
    RESTRICTED = "restricted"    # 0.2 - 0.49
    QUARANTINED = "quarantined"  # 0.0 - 0.19

    @classmethod
    def from_score(cls, score: float) -> "TrustLevel":
        if score >= 0.8:
            return cls.TRUSTED
        elif score >= 0.5:
            return cls.STANDARD
        elif score >= 0.2:
            return cls.RESTRICTED
        return cls.QUARANTINED


class ToolScope(BaseModel):
    tool_name: str
    allowed_params: dict[str, Any] = Field(default_factory=dict)
    resource_paths: list[str] = Field(default_factory=list)
    max_calls_per_minute: int = 60


class AgentIdentity(BaseModel):
    agent_id: str
    name: str
    public_key: str  # Ed25519 base64-encoded
    capability_scope: list[str]
    trust_score: float = 0.5
    trust_level: TrustLevel = TrustLevel.STANDARD
    tenant_id: str = "default"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked: bool = False


class CapabilityToken(BaseModel):
    token_id: str
    agent_id: str
    allowed_tools: list[ToolScope]
    expires_at: datetime
    signature: str
    tenant_id: str = "default"
    revoked: bool = False

    @property
    def allowed_tool_names(self) -> set[str]:
        return {t.tool_name for t in self.allowed_tools}

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
