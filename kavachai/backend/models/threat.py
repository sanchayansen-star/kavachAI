"""Kill chain and threat detection models."""

from datetime import datetime

from pydantic import BaseModel, Field


class KillChainStage(BaseModel):
    stage_number: int
    category: str  # reconnaissance | weaponization | delivery | exploitation | exfiltration | c2
    action_request_id: str
    description: str
    threat_score: float
    timestamp: datetime


class KillChain(BaseModel):
    kill_chain_id: str
    session_id: str
    stages: list[KillChainStage] = Field(default_factory=list)
    overall_threat_score: float = 0.0
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    is_stac_attack: bool = False
