"""Redis client — real-time state, pub/sub, rate limiting."""

import json
import os
from typing import Any

import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

_pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Get async Redis connection (singleton pool)."""
    global _pool
    if _pool is None:
        _pool = redis.from_url(REDIS_URL, decode_responses=True)
    return _pool


async def close_redis():
    """Close Redis connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


# --- Session state helpers ---

async def set_session_threat_score(session_id: str, score: float):
    r = await get_redis()
    await r.set(f"session:{session_id}:threat_score", str(score))


async def get_session_threat_score(session_id: str) -> float:
    r = await get_redis()
    val = await r.get(f"session:{session_id}:threat_score")
    return float(val) if val else 0.0


async def set_dfa_state(session_id: str, state_id: str):
    r = await get_redis()
    await r.set(f"session:{session_id}:dfa_state", state_id)


async def get_dfa_state(session_id: str) -> str | None:
    r = await get_redis()
    return await r.get(f"session:{session_id}:dfa_state")


async def push_action_window(session_id: str, action_hash: str, max_size: int = 50):
    r = await get_redis()
    key = f"session:{session_id}:action_window"
    await r.lpush(key, action_hash)
    await r.ltrim(key, 0, max_size - 1)


async def get_action_window(session_id: str) -> list[str]:
    r = await get_redis()
    return await r.lrange(f"session:{session_id}:action_window", 0, -1)


# --- Trust score helpers ---

async def set_trust_score(agent_id: str, score: float, level: str):
    r = await get_redis()
    await r.set(f"agent:{agent_id}:trust_score", str(score))
    await r.set(f"agent:{agent_id}:trust_level", level)


async def get_trust_score(agent_id: str) -> tuple[float, str]:
    r = await get_redis()
    score = await r.get(f"agent:{agent_id}:trust_score")
    level = await r.get(f"agent:{agent_id}:trust_level")
    return (float(score) if score else 0.5, level or "standard")


# --- Rate limiting ---

async def check_rate_limit(
    agent_id: str, tool_name: str, max_calls: int, window_seconds: int
) -> bool:
    """Returns True if within limit, False if exceeded."""
    r = await get_redis()
    key = f"rate:{agent_id}:{tool_name}:{window_seconds}"
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, window_seconds)
    return count <= max_calls


# --- Budget tracking ---

async def track_llm_cost(
    agent_id: str, session_id: str, tenant_id: str, cost: float, tokens: int
):
    r = await get_redis()
    pipe = r.pipeline()
    pipe.incrbyfloat(f"budget:{agent_id}:cost", cost)
    pipe.incrby(f"budget:{agent_id}:tokens", tokens)
    pipe.incrbyfloat(f"budget:{session_id}:cost", cost)
    pipe.incrby(f"budget:{session_id}:tokens", tokens)
    pipe.incrbyfloat(f"budget:{tenant_id}:cost", cost)
    await pipe.execute()


async def get_agent_budget(agent_id: str) -> dict[str, float]:
    r = await get_redis()
    cost = await r.get(f"budget:{agent_id}:cost")
    tokens = await r.get(f"budget:{agent_id}:tokens")
    return {"cost": float(cost or 0), "tokens": int(tokens or 0)}


# --- Dashboard pub/sub ---

async def publish_dashboard_event(tenant_id: str, event: dict[str, Any]):
    r = await get_redis()
    await r.publish(f"channel:dashboard:{tenant_id}", json.dumps(event))
