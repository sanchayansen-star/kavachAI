"""Agent Identity Manager — Ed25519 key pairs, capability tokens, verification."""

import base64
import hashlib
import json
from datetime import datetime, timedelta
from uuid import uuid4

from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError

from ..models.agent import (
    AgentIdentity,
    CapabilityToken,
    ToolScope,
    TrustLevel,
)


class AgentIdentityManager:
    """Issues, verifies, and revokes agent identities and capability tokens."""

    def __init__(self):
        self._agents: dict[str, AgentIdentity] = {}
        self._signing_keys: dict[str, SigningKey] = {}
        self._tokens: dict[str, CapabilityToken] = {}
        # KavachAI system signing key for attestations
        self._system_key = SigningKey.generate()
        self.system_public_key = self._system_key.verify_key

    def register_agent(
        self,
        name: str,
        capability_scope: list[str],
        tenant_id: str = "default",
    ) -> tuple[AgentIdentity, str]:
        """Register a new agent. Returns (identity, private_key_b64)."""
        signing_key = SigningKey.generate()
        public_key_b64 = base64.b64encode(
            bytes(signing_key.verify_key)
        ).decode()
        private_key_b64 = base64.b64encode(bytes(signing_key)).decode()

        agent_id = str(uuid4())
        identity = AgentIdentity(
            agent_id=agent_id,
            name=name,
            public_key=public_key_b64,
            capability_scope=capability_scope,
            tenant_id=tenant_id,
        )

        self._agents[agent_id] = identity
        self._signing_keys[agent_id] = signing_key
        return identity, private_key_b64

    def get_agent(self, agent_id: str) -> AgentIdentity | None:
        return self._agents.get(agent_id)

    def issue_capability_token(
        self,
        agent_id: str,
        allowed_tools: list[ToolScope],
        expires_in_seconds: int = 3600,
    ) -> CapabilityToken:
        """Issue a scoped, time-limited, signed capability token."""
        agent = self._agents.get(agent_id)
        if not agent or agent.revoked:
            raise ValueError(f"Agent {agent_id} not found or revoked")

        token_id = str(uuid4())
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)

        # Sign the token payload with KavachAI system key
        payload = json.dumps({
            "token_id": token_id,
            "agent_id": agent_id,
            "tools": [t.tool_name for t in allowed_tools],
            "expires_at": expires_at.isoformat(),
        }).encode()
        signature = base64.b64encode(
            bytes(self._system_key.sign(payload).signature)
        ).decode()

        token = CapabilityToken(
            token_id=token_id,
            agent_id=agent_id,
            allowed_tools=allowed_tools,
            expires_at=expires_at,
            signature=signature,
            tenant_id=agent.tenant_id,
        )
        self._tokens[token_id] = token
        return token

    def get_active_token(self, agent_id: str) -> CapabilityToken | None:
        """Get the most recent non-expired, non-revoked token for an agent."""
        for token in reversed(list(self._tokens.values())):
            if (
                token.agent_id == agent_id
                and not token.revoked
                and not token.is_expired()
            ):
                return token
        return None

    def verify_signature(
        self, agent_id: str, message: bytes, signature_b64: str
    ) -> bool:
        """Verify an agent's Ed25519 signature on a message."""
        agent = self._agents.get(agent_id)
        if not agent or agent.revoked:
            return False
        try:
            pub_key_bytes = base64.b64decode(agent.public_key)
            verify_key = VerifyKey(pub_key_bytes)
            sig_bytes = base64.b64decode(signature_b64)
            verify_key.verify(message, sig_bytes)
            return True
        except (BadSignatureError, Exception):
            return False

    def sign_attestation(self, payload: bytes) -> str:
        """Sign data with KavachAI's system key (for action attestations)."""
        signed = self._system_key.sign(payload)
        return base64.b64encode(bytes(signed.signature)).decode()

    def revoke_agent(self, agent_id: str) -> bool:
        """Revoke an agent identity and all its tokens."""
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        agent.revoked = True
        for token in self._tokens.values():
            if token.agent_id == agent_id:
                token.revoked = True
        return True

    def revoke_token(self, token_id: str) -> bool:
        """Revoke a specific capability token."""
        token = self._tokens.get(token_id)
        if not token:
            return False
        token.revoked = True
        return True

    @staticmethod
    def hash_agent_identity(public_key: str) -> str:
        """SHA-256 hash of agent's public key for audit trail."""
        return hashlib.sha256(public_key.encode()).hexdigest()

    def check_tool_authorized(
        self, agent_id: str, tool_name: str
    ) -> tuple[bool, str]:
        """Check if agent is authorized to call a tool. Returns (allowed, reason)."""
        agent = self._agents.get(agent_id)
        if not agent:
            return False, "AGENT_NOT_FOUND"
        if agent.revoked:
            return False, "AGENT_REVOKED"

        token = self.get_active_token(agent_id)
        if not token:
            return False, "NO_ACTIVE_TOKEN"
        if token.is_expired():
            return False, "TOKEN_EXPIRED"
        if tool_name not in token.allowed_tool_names:
            return False, "PRIVILEGE_VIOLATION"

        return True, "AUTHORIZED"
