"""KavachAI — Zero Trust Safety Firewall for Agentic AI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init DB, Redis, verify audit trail. Shutdown: cleanup."""
    from .db.database import init_db
    from .db.redis_client import get_redis, close_redis

    await init_db()
    await get_redis()  # warm up connection pool
    yield
    await close_redis()


app = FastAPI(
    title="KavachAI",
    description="Zero Trust Safety Firewall for Agentic AI",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "kavachai", "version": "0.1.0"}


# Router includes — uncomment as modules are implemented
# from .api import routes_eval, routes_session, routes_policy
# from .api import routes_escalation, routes_llm, routes_compliance
# from .api import routes_grounding, websocket
# app.include_router(routes_eval.router, prefix="/api/v1")
# app.include_router(routes_session.router, prefix="/api/v1")
# app.include_router(routes_policy.router, prefix="/api/v1")
# app.include_router(routes_escalation.router, prefix="/api/v1")
# app.include_router(routes_llm.router, prefix="/api/v1")
# app.include_router(routes_compliance.router, prefix="/api/v1")
# app.include_router(routes_grounding.router, prefix="/api/v1")
