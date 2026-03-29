"""LLM Gateway API routes."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from kavachai.backend.llm.gateway import LLMGateway, LLMRequest

router = APIRouter(prefix="/api/v1/llm", tags=["llm"])

gateway = LLMGateway()


class CompletionRequest(BaseModel):
    model: str | None = None
    messages: list[dict[str, str]]
    agent_id: str
    session_id: str


@router.post("/completions")
async def create_completion(body: CompletionRequest):
    request = LLMRequest(
        model=body.model,
        messages=body.messages,
        agent_id=body.agent_id,
        session_id=body.session_id,
    )
    response = await gateway.complete(request)
    return {
        "completion": response.content,
        "model_used": response.model_used,
        "tokens": response.tokens,
        "cost": response.cost,
        "blocked": response.blocked,
        "reason": response.reason,
    }


@router.get("/models")
async def list_models():
    return [
        {"model_name": "gpt-4", "provider": "openai", "status": "available", "cost_per_1k_tokens": 0.03},
        {"model_name": "gpt-3.5-turbo", "provider": "openai", "status": "available", "cost_per_1k_tokens": 0.001},
        {"model_name": "claude-3-sonnet", "provider": "anthropic", "status": "available", "cost_per_1k_tokens": 0.015},
    ]


@router.get("/usage")
async def get_usage(agent_id: str = ""):
    if agent_id:
        return gateway.get_usage(agent_id)
    return {"total_tokens": 0, "total_cost": 0.0}


from kavachai.backend.llm.eval_engine import LLMEvalEngine
from kavachai.backend.llm.red_team import RedTeamRunner

eval_engine = LLMEvalEngine()
red_team = RedTeamRunner()


@router.post("/evaluate/{model_name}")
async def evaluate_model(model_name: str):
    result = await eval_engine.evaluate(model_name)
    return {
        "model_name": result.model_name,
        "overall_score": result.overall_score,
        "sub_scores": result.sub_scores,
        "passed": result.passed,
        "evaluated_at": result.evaluated_at.isoformat(),
    }


@router.post("/red-team/{model_name}")
async def run_red_team(model_name: str):
    result = await red_team.run(model_name)
    return {
        "run_id": result.run_id,
        "model_name": result.model_name,
        "cases_run": result.cases_run,
        "vulnerabilities_found": result.vulnerabilities_found,
        "safety_score_delta": result.safety_score_delta,
        "degraded": result.degraded,
    }


@router.get("/evaluations/{model_name}/history")
async def get_eval_history(model_name: str):
    history = eval_engine.get_history(model_name)
    return [
        {"overall_score": r.overall_score, "sub_scores": r.sub_scores, "passed": r.passed, "evaluated_at": r.evaluated_at.isoformat()}
        for r in history
    ]
