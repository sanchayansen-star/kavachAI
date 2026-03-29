"""SHA-256 hash chain computation for audit entries."""

from __future__ import annotations

import hashlib


def compute_entry_hash(
    entry_id: int,
    timestamp: str,
    session_id: str,
    agent_identity_hash: str,
    action_params_hash: str,
    action_verdict: str,
    previous_entry_hash: str,
) -> str:
    """Compute SHA-256 hash for an audit entry.

    Hash = SHA-256(entry_id || timestamp || session_id ||
                   agent_identity_hash || action_params_hash ||
                   action_verdict || previous_entry_hash)
    """
    payload = "||".join([
        str(entry_id),
        timestamp,
        session_id,
        agent_identity_hash,
        action_params_hash,
        action_verdict,
        previous_entry_hash,
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_params_hash(params_json: str) -> str:
    """SHA-256 hash of action parameters JSON."""
    return hashlib.sha256(params_json.encode("utf-8")).hexdigest()


def compute_identity_hash(agent_id: str, public_key: str) -> str:
    """SHA-256 hash of agent identity."""
    return hashlib.sha256(f"{agent_id}:{public_key}".encode("utf-8")).hexdigest()
