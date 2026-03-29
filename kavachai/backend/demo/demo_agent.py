"""Simulated financial services AI agent with tools for demo."""

from __future__ import annotations

from typing import Any


class DemoFinancialAgent:
    """Simulated agent with financial service tools."""

    TOOLS = [
        {"name": "verify_identity", "description": "Verify customer identity via KYC"},
        {"name": "customer_lookup", "description": "Look up customer records"},
        {"name": "payment_process", "description": "Process a payment transaction"},
        {"name": "send_email", "description": "Send email to customer or external"},
        {"name": "external_api", "description": "Call external third-party API"},
        {"name": "admin_panel", "description": "Access admin panel (restricted)"},
    ]

    def execute_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        handlers = {
            "verify_identity": self._verify_identity,
            "customer_lookup": self._customer_lookup,
            "payment_process": self._payment_process,
            "send_email": self._send_email,
            "external_api": self._external_api,
            "admin_panel": self._admin_panel,
        }
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        return handler(params)

    @staticmethod
    def _verify_identity(params: dict) -> dict:
        return {"verified": True, "customer_id": params.get("customer_id", "cust-001"), "kyc_status": "complete"}

    @staticmethod
    def _customer_lookup(params: dict) -> dict:
        return {
            "customer_id": params.get("customer_id", "cust-001"),
            "name": "[name]",
            "aadhaar": "1234 5678 9012",
            "pan": "ABCDE1234F",
            "mobile": "+91 9876543210",
            "accounts": [{"id": "acc-001", "balance": 150000}],
        }

    @staticmethod
    def _payment_process(params: dict) -> dict:
        return {"transaction_id": "txn-demo-001", "amount": params.get("amount", 0), "status": "processed"}

    @staticmethod
    def _send_email(params: dict) -> dict:
        return {"sent": True, "to": params.get("to", ""), "subject": params.get("subject", "")}

    @staticmethod
    def _external_api(params: dict) -> dict:
        return {"status": 200, "data": params.get("payload", {})}

    @staticmethod
    def _admin_panel(params: dict) -> dict:
        return {"access": "granted", "panel": "admin", "action": params.get("action", "view")}
