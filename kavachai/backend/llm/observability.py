"""LLM observability — latency tracking, drift detection, model cards."""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ModelMetrics:
    latencies_ms: list[float] = field(default_factory=list)
    errors: int = 0
    refusals: int = 0
    total_requests: int = 0

    @property
    def p50(self) -> float:
        return statistics.median(self.latencies_ms) if self.latencies_ms else 0

    @property
    def p95(self) -> float:
        if not self.latencies_ms:
            return 0
        sorted_l = sorted(self.latencies_ms)
        idx = int(len(sorted_l) * 0.95)
        return sorted_l[min(idx, len(sorted_l) - 1)]

    @property
    def error_rate(self) -> float:
        return self.errors / max(self.total_requests, 1)

    @property
    def refusal_rate(self) -> float:
        return self.refusals / max(self.total_requests, 1)


@dataclass
class DriftAlert:
    model_name: str
    metric: str
    baseline: float
    current: float
    timestamp: datetime


class LLMObservability:
    """Track latency, error rate, refusal rate, and detect model drift."""

    def __init__(self) -> None:
        self._metrics: dict[str, ModelMetrics] = {}
        self._baselines: dict[str, dict[str, float]] = {}
        self._alerts: list[DriftAlert] = []

    def record(self, model_name: str, latency_ms: float, error: bool = False, refusal: bool = False) -> None:
        m = self._metrics.setdefault(model_name, ModelMetrics())
        m.latencies_ms.append(latency_ms)
        m.total_requests += 1
        if error:
            m.errors += 1
        if refusal:
            m.refusals += 1

    def set_baseline(self, model_name: str) -> None:
        m = self._metrics.get(model_name)
        if m:
            self._baselines[model_name] = {
                "latency_p95": m.p95,
                "error_rate": m.error_rate,
                "refusal_rate": m.refusal_rate,
            }

    def check_drift(self, model_name: str, threshold: float = 0.5) -> list[DriftAlert]:
        m = self._metrics.get(model_name)
        baseline = self._baselines.get(model_name)
        if not m or not baseline:
            return []

        alerts: list[DriftAlert] = []
        checks = [
            ("latency_p95", m.p95, baseline.get("latency_p95", 0)),
            ("error_rate", m.error_rate, baseline.get("error_rate", 0)),
            ("refusal_rate", m.refusal_rate, baseline.get("refusal_rate", 0)),
        ]
        for metric, current, base in checks:
            if base > 0 and abs(current - base) / base > threshold:
                alert = DriftAlert(model_name=model_name, metric=metric, baseline=base, current=current, timestamp=datetime.utcnow())
                alerts.append(alert)
                self._alerts.append(alert)
        return alerts

    def get_metrics(self, model_name: str) -> ModelMetrics | None:
        return self._metrics.get(model_name)
