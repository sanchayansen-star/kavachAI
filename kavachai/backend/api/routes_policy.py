"""Policy management API routes — upload, list, retrieve DSL policies."""

from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from kavachai.backend.core.dsl_parser import DSLParseError, parse_dsl
from kavachai.backend.db.database import get_db

router = APIRouter(prefix="/api/v1/policies", tags=["policies"])


class PolicyUploadRequest(BaseModel):
    dsl_source: str
    name: str
    tenant_id: str = "default"


class PolicyUploadResponse(BaseModel):
    policy_id: str
    name: str
    warnings: list[str] = []


class PolicySummary(BaseModel):
    policy_id: str
    name: str
    status: str
    rule_count: int


class PolicyDetail(BaseModel):
    policy_id: str
    name: str
    dsl_source: str
    ast_summary: dict
    status: str


@router.put("", response_model=PolicyUploadResponse)
async def upload_policy(body: PolicyUploadRequest):
    """Parse DSL source, store AST in SQLite, support hot reload."""
    try:
        ast = parse_dsl(body.dsl_source)
    except DSLParseError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"DSL parse error at line {exc.line}, col {exc.column}: {exc}",
        )

    ast.name = body.name
    now = datetime.utcnow().isoformat()
    ast_json = ast.model_dump_json()

    db = await get_db()
    try:
        await db.execute(
            """INSERT OR REPLACE INTO policies
               (policy_id, name, dsl_source, ast_json, status, tenant_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, 'active', ?, ?, ?)""",
            (ast.policy_id, body.name, body.dsl_source, ast_json, body.tenant_id, now, now),
        )
        await db.commit()
    finally:
        await db.close()

    return PolicyUploadResponse(policy_id=ast.policy_id, name=body.name)


@router.get("", response_model=list[PolicySummary])
async def list_policies(tenant_id: str = "default"):
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT policy_id, name, status, ast_json FROM policies WHERE tenant_id = ?",
            (tenant_id,),
        )
        rows = await cursor.fetchall()
    finally:
        await db.close()

    results = []
    for row in rows:
        ast_data = json.loads(row[3]) if row[3] else {}
        results.append(PolicySummary(
            policy_id=row[0],
            name=row[1],
            status=row[2],
            rule_count=len(ast_data.get("rules", [])),
        ))
    return results


@router.get("/{policy_id}", response_model=PolicyDetail)
async def get_policy(policy_id: str):
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT policy_id, name, dsl_source, ast_json, status FROM policies WHERE policy_id = ?",
            (policy_id,),
        )
        row = await cursor.fetchone()
    finally:
        await db.close()

    if not row:
        raise HTTPException(status_code=404, detail="Policy not found")

    ast_data = json.loads(row[3]) if row[3] else {}
    return PolicyDetail(
        policy_id=row[0],
        name=row[1],
        dsl_source=row[2],
        ast_summary={
            "rules": len(ast_data.get("rules", [])),
            "workflows": len(ast_data.get("workflows", [])),
            "imports": ast_data.get("imports", []),
        },
        status=row[4],
    )


from kavachai.backend.core.formal_verifier import FormalPolicyVerifier

_verifier = FormalPolicyVerifier()


@router.post("/{policy_id}/verify")
async def verify_policy(policy_id: str):
    """Run formal verification on a stored policy."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT ast_json FROM policies WHERE policy_id = ?", (policy_id,)
        )
        row = await cursor.fetchone()
    finally:
        await db.close()

    if not row:
        raise HTTPException(status_code=404, detail="Policy not found")

    from kavachai.backend.models.policy import PolicyAST
    ast = PolicyAST.model_validate_json(row[0])
    cert = _verifier.verify(ast)

    return {
        "consistent": cert.consistent,
        "complete": cert.complete,
        "conflicts": cert.conflicts,
        "properties_proven": cert.properties_proven,
        "policy_hash": cert.policy_hash,
    }
