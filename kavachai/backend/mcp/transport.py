"""MCP transport support — stdio and SSE."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Awaitable


class StdioTransport:
    """JSON-RPC over stdio for MCP communication."""

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer

    async def read_message(self) -> dict[str, Any] | None:
        line = await self.reader.readline()
        if not line:
            return None
        return json.loads(line.decode("utf-8").strip())

    async def write_message(self, msg: dict[str, Any]) -> None:
        data = json.dumps(msg) + "\n"
        self.writer.write(data.encode("utf-8"))
        await self.writer.drain()


class SSETransport:
    """Server-Sent Events transport for MCP over HTTP."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[..., Awaitable[Any]]] = {}

    def on(self, method: str, handler: Callable[..., Awaitable[Any]]) -> None:
        self._handlers[method] = handler

    async def handle_request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        handler = self._handlers.get(method)
        if not handler:
            return {"error": {"code": -32601, "message": f"Method not found: {method}"}}
        try:
            result = await handler(params)
            return {"result": result}
        except Exception as exc:
            return {"error": {"code": -32600, "message": str(exc)}}
