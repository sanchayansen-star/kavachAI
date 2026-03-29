"""Attack chain analysis — sliding window, cumulative effects, STAC defense, kill chain."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from kavachai.backend.models.threat import KillChain, KillChainStage

WINDOW_SIZE = 50

# Category mapping for kill chain stages
_CATEGORY_HINTS: dict[str, str] = {
    "customer_lookup": "reconnaissance",
    "verify_identity": "reconnaissance",
    "search": "reconnaissance",
    "external_api": "delivery",
    "webhook": "delivery",
    "send_email": "exfiltration",
    "export_data": "exfiltration",
    "payment_process": "exploitation",
    "transfer_funds": "exploitation",
    "admin_panel": "exploitation",
    "admin_access": "exploitation",
}


@dataclass
class ChainAnalysis:
    threat_score: float
    is_stac: bool
    kill_chain: KillChain | None
    cumulative_effects: dict[str, Any]


class AttackChainAnalyzer:
    """Sliding window (50 actions), cumulative effect model, STAC defense."""

    def __init__(self) -> None:
        # session_id -> list of action records
        self._windows: dict[str, list[dict[str, Any]]] = {}

    def analyze(
        self,
        session_id: str,
        tool_name: str,
        params: dict[str, Any],
        threat_scores: dict[str, float],
        timestamp: datetime | None = None,
    ) -> ChainAnalysis:
        ts = timestamp or datetime.utcnow()
        window = self._windows.setdefault(session_id, [])
        window.append({
            "tool_name": tool_name,
            "params": params,
            "threat_scores": threat_scores,
            "timestamp": ts,
        })

        # Keep sliding window
        if len(window) > WINDOW_SIZE:
            window[:] = window[-WINDOW_SIZE:]

        # Cumulative effects
        effects = self._compute_cumulative_effects(window)

        # Weighted threat score — recent actions contribute more
        session_score = self._compute_session_score(window)

        # STAC detection
        is_stac = self._detect_stac(window)

        # Build kill chain if enough stages detected
        kill_chain = self._build_kill_chain(session_id, window, session_score, is_stac)

        return ChainAnalysis(
            threat_score=session_score,
            is_stac=is_stac,
            kill_chain=kill_chain,
            cumulative_effects=effects,
        )

    @staticmethod
    def _compute_cumulative_effects(window: list[dict]) -> dict[str, Any]:
        tools_called = [a["tool_name"] for a in window]
        data_sources = set()
        data_flows: list[dict[str, str]] = []

        for action in window:
            tn = action["tool_name"]
            if tn in ("customer_lookup", "search", "query"):
                data_sources.add(tn)
            if tn in ("send_email", "external_api", "webhook"):
                for src in data_sources:
                    data_flows.append({"source": src, "destination": "external"})

        return {
            "tools_called": tools_called,
            "data_accessed": list(data_sources),
            "data_flows": data_flows,
        }

    @staticmethod
    def _compute_session_score(window: list[dict]) -> float:
        if not window:
            return 0.0
        total_weight = 0.0
        weighted_sum = 0.0
        for i, action in enumerate(window):
            weight = (i + 1) / len(window)  # More recent = higher weight
            max_threat = max(action["threat_scores"].values()) if action["threat_scores"] else 0.0
            weighted_sum += max_threat * weight
            total_weight += weight
        return min(weighted_sum / total_weight, 1.0) if total_weight > 0 else 0.0

    @staticmethod
    def _detect_stac(window: list[dict]) -> bool:
        """Detect Sequential Tool Attack Chain — individually benign, collectively harmful."""
        if len(window) < 3:
            return False
        # Check if individual scores are low but cumulative pattern is suspicious
        individual_scores = []
        for a in window[-5:]:
            s = max(a["threat_scores"].values()) if a["threat_scores"] else 0.0
            individual_scores.append(s)
        avg_individual = sum(individual_scores) / len(individual_scores) if individual_scores else 0
        # STAC: low individual scores but diverse tool usage suggesting coordinated attack
        unique_tools = len(set(a["tool_name"] for a in window[-5:]))
        return avg_individual < 0.4 and unique_tools >= 3

    @staticmethod
    def _build_kill_chain(
        session_id: str,
        window: list[dict],
        threat_score: float,
        is_stac: bool,
    ) -> KillChain | None:
        if len(window) < 2:
            return None

        stages: list[KillChainStage] = []
        seen_categories: set[str] = set()

        for i, action in enumerate(window):
            category = _CATEGORY_HINTS.get(action["tool_name"], "unknown")
            if category != "unknown" and category not in seen_categories:
                seen_categories.add(category)
                stages.append(KillChainStage(
                    stage_number=len(stages) + 1,
                    category=category,
                    action_request_id="",
                    description=f'{action["tool_name"]} call',
                    threat_score=max(action["threat_scores"].values()) if action["threat_scores"] else 0.0,
                    timestamp=action["timestamp"],
                ))

        if len(stages) < 2:
            return None

        return KillChain(
            kill_chain_id="",
            session_id=session_id,
            stages=stages,
            overall_threat_score=threat_score,
            detected_at=datetime.utcnow(),
            is_stac_attack=is_stac,
        )
