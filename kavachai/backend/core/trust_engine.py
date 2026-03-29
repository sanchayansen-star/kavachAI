"""Dynamic trust scoring engine — severity-weighted violations, time decay, graduated enforcement."""

from __future__ import annotations

from enum import Enum
from typing import Any

from kavachai.backend.models.agent import TrustLevel


# Severity weights for trust score impact
_SEVERITY_WEIGHTS = {
    "critical": 0.3,
    "high": 0.2,
    "medium": 0.1,
    "low": 0.05,
}

# Trust level thresholds
_TRUST_THRESHOLDS = [
    (0.8, TrustLevel.TRUSTED),
    (0.5, TrustLevel.STANDARD),
    (0.2, TrustLevel.RESTRICTED),
    (0.0, TrustLevel.QUARANTINED),
]

# Time decay factor per evaluation (small recovery toward 0.5)
_DECAY_FACTOR = 0.01


class TrustEngine:
    """Dynamic trust score computation with graduated enforcement."""

    def __init__(self) -> None:
        # agent_id -> current trust score
        self._scores: dict[str, float] = {}

    def get_score(self, agent_id: str) -> float:
        return self._scores.get(agent_id, 0.5)

    def get_level(self, agent_id: str) -> TrustLevel:
        score = self.get_score(agent_id)
        return self._score_to_level(score)

    def initialize(self, agent_id: str, score: float = 0.5) -> None:
        self._scores[agent_id] = max(0.0, min(1.0, score))

    def update_on_violation(self, agent_id: str, severity: str) -> tuple[float, float]:
        """Decrease trust score based on violation severity.

        Returns (old_score, new_score).
        """
        old = self.get_score(agent_id)
        penalty = _SEVERITY_WEIGHTS.get(severity, 0.1)
        new = max(0.0, old - penalty)
        self._scores[agent_id] = new
        return old, new

    def update_on_success(self, agent_id: str) -> tuple[float, float]:
        """Slightly increase trust score on successful action (time decay toward baseline)."""
        old = self.get_score(agent_id)
        # Small recovery, capped at 1.0
        new = min(1.0, old + _DECAY_FACTOR)
        self._scores[agent_id] = new
        return old, new

    @staticmethod
    def _score_to_level(score: float) -> TrustLevel:
        for threshold, level in _TRUST_THRESHOLDS:
            if score >= threshold:
                return level
        return TrustLevel.QUARANTINED
