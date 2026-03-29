"""Cryptographic audit trail — append entries with hash chain linking."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from kavachai.backend.audit.hash_chain import compute_entry_hash, compute_params_hash
from kavachai.backend.db.database import get_db
from kavachai.backend.models.action import VerdictType

MAX_RETRIES = 3


class AuditTrailError(Exception):
    pass


class CryptographicAuditTrail:
    """Append-only audit trail with SHA-256 hash chain linking.

    - Monotonic sequence numbers per session
    - Integrity verification
    - Retry logic (3 retries, halt session on failure)
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
    ) -> int:
        """Append an entry to the audit trail. Returns the entry_id."""
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
                    matched_policies=json.dumps(matched_policies or []),
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

    async def _do_append(self, **kwargs) -> int:
        db = await get_db()
        try:
            # Get previous entry for this session
            cursor = await db.execute(
                """SELECT entry_id, entry_hash, sequence_number
                   FROM audit_entries
                   WHERE session_id = ?
                   ORDER BY sequence_number DESC LIMIT 1""",
                (kwargs["session_id"],),
            )
            prev = await cursor.fetchone()

            if prev:
                prev_hash = prev[1]
                seq = prev[2] + 1
            else:
                prev_hash = ""
                seq = 1

            # We need a temporary entry_id for hash computation; use seq as proxy
            entry_hash = compute_entry_hash(
                entry_id=seq,
                timestamp=kwargs["timestamp"],
                session_id=kwargs["session_id"],
                agent_identity_hash=kwargs["agent_identity_hash"],
                action_params_hash=kwargs["params_hash"],
                action_verdict=kwargs["verdict"],
                previous_entry_hash=prev_hash,
            )

            cursor = await db.execute(
                """INSERT INTO audit_entries
                   (timestamp, session_id, tenant_id, agent_identity_hash,
                    action_type, action_params_hash, action_verdict,
                    matched_policies, threat_score, ethics_score, grounding_score,
                    trust_score_before, trust_score_after,
                    previous_entry_hash, entry_hash, sequence_number)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    kwargs["timestamp"],
                    kwargs["session_id"],
                    kwargs["tenant_id"],
                    kwargs["agent_identity_hash"],
                    kwargs["action_type"],
                    kwargs["params_hash"],
                    kwargs["verdict"],
                    kwargs["matched_policies"],
                    kwargs["threat_score"],
                    kwargs["ethics_score"],
                    kwargs["grounding_score"],
                    kwargs["trust_score_before"],
                    kwargs["trust_score_after"],
                    prev_hash,
                    entry_hash,
                    seq,
                ),
            )
            await db.commit()
            return cursor.lastrowid or seq
        finally:
            await db.close()

    async def verify_chain(self, session_id: str) -> bool:
        """Verify hash chain integrity for a session."""
        db = await get_db()
        try:
            cursor = await db.execute(
                """SELECT entry_id, timestamp, session_id, agent_identity_hash,
                          action_params_hash, action_verdict, previous_entry_hash,
                          entry_hash, sequence_number
                   FROM audit_entries
                   WHERE session_id = ?
                   ORDER BY sequence_number ASC""",
                (session_id,),
            )
            rows = await cursor.fetchall()
        finally:
            await db.close()

        if not rows:
            return True

        prev_hash = ""
        prev_seq = 0
        for row in rows:
            entry_id, ts, sid, agent_hash, params_hash, verdict, stored_prev, stored_hash, seq = row

            # Check monotonic sequence
            if seq <= prev_seq and prev_seq > 0:
                return False

            # Check previous hash link
            if stored_prev != prev_hash:
                return False

            # Recompute hash
            expected = compute_entry_hash(
                entry_id=seq,
                timestamp=ts,
                session_id=sid,
                agent_identity_hash=agent_hash,
                action_params_hash=params_hash,
                action_verdict=verdict,
                previous_entry_hash=stored_prev,
            )
            if expected != stored_hash:
                return False

            prev_hash = stored_hash
            prev_seq = seq

        return True
