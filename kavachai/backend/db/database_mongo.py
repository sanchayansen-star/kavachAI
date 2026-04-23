"""MongoDB Atlas database adapter for KavachAI.

Drop-in replacement for the SQLite database layer. Uses Motor (async MongoDB driver)
to provide the same data access patterns with MongoDB Atlas as the backend.

Collections:
    audit_entries       — Hash-chain audit trail (append-only)
    agents              — Agent registrations
    capability_tokens   — Scoped, signed capability tokens
    policies            — DSL policies with compiled ASTs
    dfa_models          — DFA behavioral models
    kill_chains         — Detected attack kill chains
    escalations         — Human-in-the-loop escalation queue
    model_evaluations   — LLM safety evaluation results
    red_team_runs       — Adversarial red team results
    knowledge_graphs    — Semantic grounding knowledge graphs
    domain_ontologies   — Domain ontology definitions
    grounding_results   — Semantic grounding validation results
    tenants             — Multi-tenant isolation

Usage:
    Set DATABASE_BACKEND=mongodb and MONGODB_URI in config or environment.
    from kavachai.backend.db.database_mongo import get_db, init_db
"""

from __future__ import annotations

import os
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://localhost:27017/kavachai?retryWrites=true&w=majority",
)
_DB_NAME = os.getenv("MONGODB_DATABASE", "kavachai")

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def get_client() -> AsyncIOMotorClient:
    """Get or create the shared Motor client."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(_MONGODB_URI)
    return _client


async def get_db() -> AsyncIOMotorDatabase:
    """Get the KavachAI MongoDB database instance."""
    global _db
    if _db is None:
        client = await get_client()
        _db = client[_DB_NAME]
    return _db


async def close_db() -> None:
    """Close the MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None


async def init_db() -> None:
    """Initialize MongoDB collections and indexes.

    Creates indexes that mirror the SQLite schema's indexes and constraints.
    MongoDB collections are created implicitly on first insert, but indexes
    must be created explicitly.
    """
    db = await get_db()

    # ── audit_entries ──
    audit = db["audit_entries"]
    await audit.create_index(
        [("session_id", 1), ("sequence_number", 1)],
        unique=True,
        name="idx_audit_session_seq",
    )
    await audit.create_index(
        [("tenant_id", 1), ("timestamp", -1)],
        name="idx_audit_tenant_time",
    )
    await audit.create_index(
        [("agent_identity_hash", 1), ("timestamp", -1)],
        name="idx_audit_agent_time",
    )
    await audit.create_index("entry_hash", unique=True, name="idx_audit_hash")

    # ── agents ──
    agents = db["agents"]
    await agents.create_index("agent_id", unique=True, name="idx_agent_id")
    await agents.create_index("tenant_id", name="idx_agent_tenant")

    # ── capability_tokens ──
    tokens = db["capability_tokens"]
    await tokens.create_index("token_id", unique=True, name="idx_token_id")
    await tokens.create_index("agent_id", name="idx_token_agent")

    # ── policies ──
    policies = db["policies"]
    await policies.create_index("policy_id", unique=True, name="idx_policy_id")
    await policies.create_index(
        [("tenant_id", 1), ("status", 1)],
        name="idx_policy_tenant_status",
    )

    # ── kill_chains ──
    kc = db["kill_chains"]
    await kc.create_index("kill_chain_id", unique=True, name="idx_kc_id")
    await kc.create_index("session_id", name="idx_kc_session")

    # ── escalations ──
    esc = db["escalations"]
    await esc.create_index("escalation_id", unique=True, name="idx_esc_id")
    await esc.create_index(
        [("status", 1), ("threat_score", -1)],
        name="idx_esc_status_threat",
    )

    # ── model_evaluations ──
    evals = db["model_evaluations"]
    await evals.create_index("evaluation_id", unique=True, name="idx_eval_id")
    await evals.create_index(
        [("model_name", 1), ("evaluated_at", -1)],
        name="idx_eval_model_time",
    )

    # ── grounding_results ──
    gr = db["grounding_results"]
    await gr.create_index("result_id", unique=True, name="idx_gr_id")
    await gr.create_index(
        [("session_id", 1), ("created_at", -1)],
        name="idx_gr_session_time",
    )

    # ── tenants ──
    tenants = db["tenants"]
    await tenants.create_index("tenant_id", unique=True, name="idx_tenant_id")


# ═══════════════════════════════════════════════════════════════
# Collection helper classes — typed wrappers for common operations
# ═══════════════════════════════════════════════════════════════


class AuditCollection:
    """Typed wrapper for the audit_entries collection."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["audit_entries"]

    async def append(self, entry: dict[str, Any]) -> str:
        """Insert an audit entry. Returns the inserted _id as string."""
        result = await self._col.insert_one(entry)
        return str(result.inserted_id)

    async def get_session_entries(
        self, session_id: str, start: str | None = None, end: str | None = None
    ) -> list[dict[str, Any]]:
        """Get all audit entries for a session, ordered by sequence number."""
        query: dict[str, Any] = {"session_id": session_id}
        if start:
            query.setdefault("timestamp", {})["$gte"] = start
        if end:
            query.setdefault("timestamp", {})["$lte"] = end

        cursor = self._col.find(query).sort("sequence_number", 1)
        return [doc async for doc in cursor]

    async def get_last_entry(self, session_id: str) -> dict[str, Any] | None:
        """Get the most recent audit entry for a session."""
        cursor = (
            self._col.find({"session_id": session_id})
            .sort("sequence_number", -1)
            .limit(1)
        )
        entries = [doc async for doc in cursor]
        return entries[0] if entries else None


class AgentCollection:
    """Typed wrapper for the agents collection."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["agents"]

    async def insert(self, agent: dict[str, Any]) -> None:
        await self._col.insert_one(agent)

    async def find_by_id(self, agent_id: str) -> dict[str, Any] | None:
        return await self._col.find_one({"agent_id": agent_id})

    async def update(self, agent_id: str, updates: dict[str, Any]) -> None:
        await self._col.update_one({"agent_id": agent_id}, {"$set": updates})

    async def find_by_tenant(self, tenant_id: str) -> list[dict[str, Any]]:
        cursor = self._col.find({"tenant_id": tenant_id})
        return [doc async for doc in cursor]


class PolicyCollection:
    """Typed wrapper for the policies collection."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["policies"]

    async def upsert(self, policy: dict[str, Any]) -> None:
        await self._col.replace_one(
            {"policy_id": policy["policy_id"]}, policy, upsert=True
        )

    async def find_by_id(self, policy_id: str) -> dict[str, Any] | None:
        return await self._col.find_one({"policy_id": policy_id})

    async def find_by_tenant(self, tenant_id: str) -> list[dict[str, Any]]:
        cursor = self._col.find({"tenant_id": tenant_id})
        return [doc async for doc in cursor]


class EscalationCollection:
    """Typed wrapper for the escalations collection."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["escalations"]

    async def insert(self, escalation: dict[str, Any]) -> None:
        await self._col.insert_one(escalation)

    async def find_pending(self, tenant_id: str | None = None) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"status": "pending"}
        if tenant_id:
            query["tenant_id"] = tenant_id
        cursor = self._col.find(query).sort("threat_score", -1)
        return [doc async for doc in cursor]

    async def resolve(self, escalation_id: str, updates: dict[str, Any]) -> None:
        await self._col.update_one(
            {"escalation_id": escalation_id}, {"$set": updates}
        )


class KillChainCollection:
    """Typed wrapper for the kill_chains collection."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["kill_chains"]

    async def insert(self, kill_chain: dict[str, Any]) -> None:
        await self._col.insert_one(kill_chain)

    async def find_by_session(self, session_id: str) -> list[dict[str, Any]]:
        cursor = self._col.find({"session_id": session_id}).sort("detected_at", -1)
        return [doc async for doc in cursor]


class GroundingCollection:
    """Typed wrapper for the grounding_results collection."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["grounding_results"]

    async def insert(self, result: dict[str, Any]) -> None:
        await self._col.insert_one(result)

    async def find_latest(self, session_id: str) -> dict[str, Any] | None:
        cursor = (
            self._col.find({"session_id": session_id})
            .sort("created_at", -1)
            .limit(1)
        )
        results = [doc async for doc in cursor]
        return results[0] if results else None


class TenantCollection:
    """Typed wrapper for the tenants collection."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["tenants"]

    async def insert(self, tenant: dict[str, Any]) -> None:
        await self._col.insert_one(tenant)

    async def find_by_id(self, tenant_id: str) -> dict[str, Any] | None:
        return await self._col.find_one({"tenant_id": tenant_id})

    async def find_by_api_key_hash(self, key_hash: str) -> dict[str, Any] | None:
        return await self._col.find_one({"api_key_hash": key_hash})

    async def find_all(self) -> list[dict[str, Any]]:
        cursor = self._col.find()
        return [doc async for doc in cursor]


# ═══════════════════════════════════════════════════════════════
# Convenience: get all typed collections at once
# ═══════════════════════════════════════════════════════════════


class MongoCollections:
    """Access all KavachAI MongoDB collections through typed wrappers."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.audit = AuditCollection(db)
        self.agents = AgentCollection(db)
        self.policies = PolicyCollection(db)
        self.escalations = EscalationCollection(db)
        self.kill_chains = KillChainCollection(db)
        self.grounding = GroundingCollection(db)
        self.tenants = TenantCollection(db)


async def get_collections() -> MongoCollections:
    """Get typed collection wrappers for all KavachAI collections."""
    db = await get_db()
    return MongoCollections(db)
