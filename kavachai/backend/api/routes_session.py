"""Session and audit trail API routes."""

from __future__ import annotations

from fastapi import APIRouter

from kavachai.backend.audit.evidence import generate_evidence_package
from kavachai.backend.audit.trail import CryptographicAuditTrail
from kavachai.backend.db.database import get_db

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.get("/{session_id}/audit-trail")
async def get_audit_trail(session_id: str, start: str | None = None, end: str | None = None):
    """Get audit trail for a session with hash chain verification."""
    trail = CryptographicAuditTrail()
    chain_valid = await trail.verify_chain(session_id)

    db = await get_db()
    try:
        query = "SELECT * FROM audit_entries WHERE session_id = ?"
        params: list = [session_id]
        if start:
            query += " AND timestamp >= ?"
            params.append(start)
        if end:
            query += " AND timestamp <= ?"
            params.append(end)
        query += " ORDER BY sequence_number ASC"

        cursor = await db.execute(query, params)
        columns = [d[0] for d in cursor.description] if cursor.description else []
        rows = await cursor.fetchall()
    finally:
        await db.close()

    entries = [dict(zip(columns, row)) for row in rows]
    return {"entries": entries, "hash_chain_valid": chain_valid}


@router.get("/{session_id}/evidence-package")
async def export_evidence(session_id: str, start: str | None = None, end: str | None = None):
    """Export evidence package for a session."""
    pkg = await generate_evidence_package(session_id, start, end)
    return pkg.to_dict()
