"""Grounding report API routes."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from kavachai.backend.db.database import get_db

router = APIRouter(prefix="/api/v1/sessions", tags=["grounding"])


@router.get("/{session_id}/grounding-report")
async def get_grounding_report(session_id: str):
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM grounding_results WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
            (session_id,),
        )
        row = await cursor.fetchone()
    finally:
        await db.close()

    if not row:
        return {"session_id": session_id, "grounding_score": None, "claims": [], "message": "No grounding data"}

    columns = [d[0] for d in cursor.description] if cursor.description else []
    data = dict(zip(columns, row))
    data["claims"] = json.loads(data.get("claims", "[]"))
    data["deterministic_checks"] = json.loads(data.get("deterministic_checks", "[]"))
    return data
