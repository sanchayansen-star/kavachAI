"""WebSocket endpoint for real-time SOC dashboard feed."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Connected clients: ws -> tenant_id
_clients: dict[WebSocket, str] = {}


@router.websocket("/ws/dashboard")
async def dashboard_ws(ws: WebSocket, api_key: str = ""):
    """WebSocket endpoint for real-time dashboard events.

    Event types: threat_update, escalation, kill_chain, quarantine,
                 trust_change, grounding_alert, model_drift,
                 safety_degradation, budget_warning.
    """
    await ws.accept()
    tenant_id = "default"  # Would resolve from api_key in production
    _clients[ws] = tenant_id

    try:
        while True:
            # Keep connection alive; client can send pings
            data = await ws.receive_text()
            # Echo back as acknowledgment
            await ws.send_json({"type": "ack", "data": data})
    except WebSocketDisconnect:
        _clients.pop(ws, None)


async def broadcast_event(tenant_id: str, event: dict[str, Any]) -> None:
    """Broadcast an event to all connected dashboard clients for a tenant."""
    disconnected = []
    for ws, tid in _clients.items():
        if tid == tenant_id:
            try:
                await ws.send_json(event)
            except Exception:
                disconnected.append(ws)
    for ws in disconnected:
        _clients.pop(ws, None)
