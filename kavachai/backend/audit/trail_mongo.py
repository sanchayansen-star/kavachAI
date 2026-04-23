"""MongoDB-backed cryptographic audit trail — hash chain with Motor async driver."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from kavachai.backend.audit.hash_chain import compute_entry_hash, compute_params_hash
from kavachai.backend.db.database_mongo import get_db
from kavachai.backend.models.action import VerdictType

MAX_RETRIES = 3


class AuditTrailError(Exception):
    pass


class MongoAuditTrail:
    """Append-only audit trail backed by MongoDB Atlas.

    Same interface as CryptographicAuditTrail (SQLite version) but stores
    entries in MongoDB's audit_entries collection. Hash chain integrity
    is maintained identically — each entry links to the previous via SHA-256.
    """

    async def append(
        self,
        session_id: str,
        tenant_id: str,
        agent_identity_hash: str,
        action_type: str,
        parameters: dict[str, Any],
        verdict: VerdictType,
        matched_policies: list[str] | None = None,
        threat_score: float = 0.0,
        ethics_score: float | None = None,
        grounding_score: float | None = None,
        trust_score_before: float | None = None,
        trust_score_after: float | None = None,
    ) -> str:
        """Append an entry to the audit trail. Returns the MongoDB _id."""
        params_hash = compute_params_hash(json.dumps(parameters, sort_keys=True))
        timestamp = datetime.utcnow().isoformat()

        for attempt in range(MAX_RETRIES):
            try:
                return await self._do_append(
                    session_id=session_id,
                    tenant_id=tenant_id,
                    timestamp=timestamp,
                    agent_identity_hash=agent_identity_hash,
                    action_type=action_type,
                    params_hash=params_hash,
                    verdict=verdict.value,
                    matched_policies=matched_policies or [],
                    threat_score=threat_score,
                    ethics_score=ethics_score,
                    grounding_score=grounding_score,
                    trust_score_before=trust_score_before,
                    trust_score_after=trust_score_after,
                )
            except Exception as exc:
                if attempt == MAX_RETRIES - 1:
                    raise AuditTrailError(
                        f"Failed to append audit entry after {MAX_RETRIES} retries: {exc}"
                    ) from exc
        raise AuditTrailError("Unreachable")

    async def _do_append(self, **kwargs: Any) -> str:
        db = await get_db()
        col = db["audit_entries"]

        # Get previous entry for this session
        cursor = (
            col.find({"session_id": kwargs["session_id"]})
            .sort("sequence_number", -1)
            .limit(1)
        )
        prev_entries = [doc async for doc in cursor]

        if prev_entries:
            prev_hash = prev_entries[0]["entry_hash"]
            seq = prev_entries[0]["sequence_number"] + 1
        else:
            prev_hash = ""
            seq = 1

        entry_hash = compute_entry_hash(
            entry_id=seq,
            timestamp=kwargs["timestamp"],
            session_id=kwargs["session_id"],
            agent_identity_hash=kwargs["agent_identity_hash"],
            action_params_hash=kwargs["params_hash"],
            action_verdict=kwargs["verdict"],
            previous_entry_hash=prev_hash,
        )

        doc = {
            "timestamp": kwargs["timestamp"],
            "session_id": kwargs["session_id"],
            "tenant_id": kwargs["tenant_id"],
            "agent_identity_hash": kwargs["agent_identity_hash"],
            "action_type": kwargs["action_type"],
            "action_params_hash": kwargs["params_hash"],
            "action_verdict": kwargs["verdict"],
            "matched_policies": kwargs["matched_policies"],
            "threat_score": kwargs["threat_score"],
            "ethics_score": kwargs["ethics_score"],
            "grounding_score": kwargs["grounding_score"],
            "trust_score_before": kwargs["trust_score_before"],
            "trust_score_after": kwargs["trust_score_after"],
            "previous_entry_hash": prev_hash,
            "entry_hash": entry_hash,
            "sequence_number": seq,
        }

        result = await col.insert_one(doc)
        return str(result.inserted_id)

    async def verify_chain(self, session_id: str) -> bool:
        """Verify hash chain integrity for a session."""
        db = await get_db()
        col = db["audit_entries"]

        cursor = (
            col.find({"session_id": session_id})
            .sort("sequence_number", 1)
        )
        entries = [doc async for doc in cursor]

        if not entries:
            return True

        prev_hash = ""
        prev_seq = 0
        for entry in entries:
            seq = entry["sequence_number"]

            if seq <= prev_seq and prev_seq > 0:
                return False
            if entry["previous_entry_hash"] != prev_hash:
                return False

            expected = compute_entry_hash(
                entry_id=seq,
                timestamp=entry["timestamp"],
                session_id=entry["session_id"],
                agent_identity_hash=entry["agent_identity_hash"],
                action_params_hash=entry["action_params_hash"],
                action_verdict=entry["action_verdict"],
                previous_entry_hash=entry["previous_entry_hash"],
            )
            if expected != entry["entry_hash"]:
                return False

            prev_hash = entry["entry_hash"]
            prev_seq = seq

        return True
