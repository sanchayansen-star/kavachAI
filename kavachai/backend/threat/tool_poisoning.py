"""Tool poisoning detection — schema/statistical deviation in tool responses."""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PoisoningResult:
    detected: bool
    score: float
    deviations: list[str]


class ToolPoisoningDetector:
    """Detect anomalous tool responses that may indicate tool poisoning."""

    def __init__(self) -> None:
        # tool_name -> list of response sizes (for statistical baseline)
        self._baselines: dict[str, list[int]] = {}

    def record_baseline(self, tool_name: str, response: Any) -> None:
        size = len(json.dumps(response)) if not isinstance(response, (int, float)) else 1
        self._baselines.setdefault(tool_name, []).append(size)

    def detect(self, tool_name: str, response: Any, expected_schema: dict | None = None) -> PoisoningResult:
        deviations: list[str] = []
        score = 0.0

        resp_str = json.dumps(response) if not isinstance(response, str) else response
        resp_size = len(resp_str)

        # Statistical deviation check
        baseline = self._baselines.get(tool_name, [])
        if len(baseline) >= 5:
            mean = statistics.mean(baseline)
            stdev = statistics.stdev(baseline) or 1.0
            z_score = abs(resp_size - mean) / stdev
            if z_score > 3:
                deviations.append(f"response_size_anomaly (z={z_score:.1f})")
                score = max(score, min(z_score / 5, 1.0))

        # Schema deviation check
        if expected_schema and isinstance(response, dict):
            expected_keys = set(expected_schema.get("properties", {}).keys())
            actual_keys = set(response.keys())
            extra = actual_keys - expected_keys
            if extra:
                deviations.append(f"unexpected_fields: {extra}")
                score = max(score, 0.6)

        # Embedded instruction check
        if any(kw in resp_str.lower() for kw in ["ignore previous", "system:", "admin:"]):
            deviations.append("embedded_instruction_in_response")
            score = max(score, 0.9)

        self.record_baseline(tool_name, response)

        return PoisoningResult(detected=len(deviations) > 0, score=score, deviations=deviations)
