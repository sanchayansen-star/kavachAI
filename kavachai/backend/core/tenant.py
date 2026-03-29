"""Multi-tenant isolation — tenant management, scoping, rate limiting."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from kavachai.backend.db.database import get_db


@dataclass
class Tenant:
    tenant_id: str
    name: str
    api_key_hash: str
    llm_budget: float | None = None
    rate_limit: int | None = None  # max actions per minute
    config: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""


class TenantManager:
    """Manage tenants with isolation, API key auth, and rate limits."""

    def __init__(self) -> None:
        self._tenants: dict[str, Tenant] = {}

    async def create_tenant(self, name: str, rate_limit: int = 1000, llm_budget: float = 100.0) -> tuple[Tenant, str]:
        """Create a new tenant. Returns (tenant, raw_api_key)."""
        tenant_id = str(uuid.uuid4())
        raw_key = f"kv_{uuid.uuid4().hex}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            api_key_hash=key_hash,
            llm_budget=llm_budget,
            rate_limit=rate_limit,
            created_at=datetime.utcnow().isoformat(),
        )

        # Store in DB
        db = await get_db()
        try:
            await db.execute(
                """INSERT INTO tenants (tenant_id, name, api_key_hash, llm_budget, rate_limit, config, created_at)
                   VALUES (?, ?, ?, ?, ?, '{}', ?)""",
                (tenant.tenant_id, tenant.name, tenant.api_key_hash, tenant.llm_budget, tenant.rate_limit, tenant.created_at),
            )
            await db.commit()
        finally:
            await db.close()

        self._tenants[tenant_id] = tenant
        return tenant, raw_key

    async def authenticate(self, api_key: str) -> Tenant | None:
        """Authenticate a request by API key."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Check cache first
        for t in self._tenants.values():
            if t.api_key_hash == key_hash:
                return t

        # Check DB
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT tenant_id, name, api_key_hash, llm_budget, rate_limit, created_at FROM tenants WHERE api_key_hash = ?",
                (key_hash,),
            )
            row = await cursor.fetchone()
        finally:
            await db.close()

        if not row:
            return None

        tenant = Tenant(
            tenant_id=row[0], name=row[1], api_key_hash=row[2],
            llm_budget=row[3], rate_limit=row[4], created_at=row[5],
        )
        self._tenants[tenant.tenant_id] = tenant
        return tenant

    async def get_all(self) -> list[Tenant]:
        """Get all tenants (super-admin view)."""
        db = await get_db()
        try:
            cursor = await db.execute("SELECT tenant_id, name, api_key_hash, llm_budget, rate_limit, created_at FROM tenants")
            rows = await cursor.fetchall()
        finally:
            await db.close()

        return [
            Tenant(tenant_id=r[0], name=r[1], api_key_hash=r[2], llm_budget=r[3], rate_limit=r[4], created_at=r[5])
            for r in rows
        ]
