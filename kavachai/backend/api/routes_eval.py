"""Agent registration and core evaluation API routes."""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from ..core.identity import AgentIdentityManager
from ..core.pipeline import EvalPipeline
from ..core.policy_engine import PolicyEngine
from ..models.action import ActionRequest, ActionVerdict
from ..models.agent import ToolScope
from ..threat.detector import ThreatDetector

router = APIRouter(tags=["agents"])

# Singleton instances (will be replaced with DI later)
identity_mgr = AgentIdentityManager()
policy_engine = PolicyEngine()
threat_detector = ThreatDetector()
eval_pipeline = EvalPipeline(
    identity_mgr=identity_mgr,
    policy_engine=policy_engine,
    threat_detector=threat_detector,
)


class RegisterAgentRequest(BaseModel):
    name: str
    capability_scope: list[str]
    tenant_id: str = "default"


class RegisterAgentResponse(BaseModel):
    agent_id: str
    public_key: str
    private_key: str
    capability_token_id: str


class IssueTokenRequest(BaseModel):
    allowed_tools: list[ToolScope]
    expires_in_seconds: int = 3600


@router.post("/agents/register", response_model=RegisterAgentResponse)
async def register_agent(
    req: RegisterAgentRequest,
    x_api_key: str = Header(...),
):
    """Register a new agent and return identity + initial capability token."""
    identity, private_key = identity_mgr.register_agent(
        name=req.name,
        capability_scope=req.capability_scope,
        tenant_id=req.tenant_id,
    )

    # Issue default token with declared scope
    default_tools = [
        ToolScope(tool_name=t) for t in req.capability_scope
    ]
    token = identity_mgr.issue_capability_token(
        agent_id=identity.agent_id,
        allowed_tools=default_tools,
    )

    return RegisterAgentResponse(
        agent_id=identity.agent_id,
        public_key=identity.public_key,
        private_key=private_key,
        capability_token_id=token.token_id,
    )


@router.put("/agents/{agent_id}/capabilities")
async def update_capabilities(
    agent_id: str,
    req: IssueTokenRequest,
    x_api_key: str = Header(...),
):
    """Issue a new capability token with updated tool scopes."""
    try:
        token = identity_mgr.issue_capability_token(
            agent_id=agent_id,
            allowed_tools=req.allowed_tools,
            expires_in_seconds=req.expires_in_seconds,
        )
        return {"token_id": token.token_id, "expires_at": token.expires_at.isoformat()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/agents/{agent_id}")
async def revoke_agent(
    agent_id: str,
    x_api_key: str = Header(...),
):
    """Revoke an agent identity and all its tokens."""
    success = identity_mgr.revoke_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"revoked": True, "agent_id": agent_id}


@router.post("/evaluate", response_model=ActionVerdict)
async def evaluate_action(
    request: ActionRequest,
    x_api_key: str = Header(...),
):
    """Run an ActionRequest through the Zero Trust evaluation pipeline."""
    verdict = await eval_pipeline.evaluate(request)
    return verdict
