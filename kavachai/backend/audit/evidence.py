"""Evidence package generation — export audit entries with hash chain proof."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from kavachai.backend.audit.trail import CryptographicAuditTrail
from kavachai.backend.db.database import get_db


class EvidencePackage:
    """Cryptographically signed evidence bundle for forensic export."""

    def __init__(
        self,
        session_id: str,
        entries: list[dict[str, Any]],
        chain_valid: bool,
        exported_at: str,
        package_hash: str,
    ):
        self.session_id = session_id
        self.entries = entries
        self.chain_valid = chain_valid
        self.exported_at = exported_at
        self.package_hash = package_hash

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "entries": self.entries,
            "chain_of_custody": {
                "hash_chain_valid": self.chain_valid,
                "entry_count": len(self.entries),
                "exported_at": self.exported_at,
            },
            "package_hash": self.package_hash,
        }


async def generate_evidence_package(
    session_id: str,
    start: str | None = None,
    end: str | None = None,
) -> EvidencePackage:
    """Export session audit entries with hash chain proof."""
    trail = CryptographicAuditTrail()
    chain_valid = await trail.verify_chain(session_id)

    db = await get_db()
    try:
        query = "SELECT * FROM audit_entries WHERE session_id = ?"
        params: list[Any] = [session_id]
        if start:
            query += " AND timestamp >= ?"
            params.append(start)
        if end:
            query += " AND timestamp <= ?"
            params.append(end)
        query += " ORDER BY sequence_number ASC"

        cursor = await db.execute(query, params)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = await cursor.fetchall()
    finally:
        await db.close()

    entries = [dict(zip(columns, row)) for row in rows]
    exported_at = datetime.utcnow().isoformat()

    # Package hash for tamper detection
    payload = json.dumps({"session_id": session_id, "entries": entries, "exported_at": exported_at}, sort_keys=True)
    package_hash = hashlib.sha256(payload.encode()).hexdigest()

    return EvidencePackage(
        session_id=session_id,
        entries=entries,
        chain_valid=chain_valid,
        exported_at=exported_at,
        package_hash=package_hash,
    )
