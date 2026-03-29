"""DPDP Act 2023 compliance engine — consent, localization, breach notification."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ConsentRecord:
    data_principal_id: str
    purpose: str
    granted: bool
    granted_at: datetime | None = None
    expires_at: datetime | None = None


@dataclass
class DPDPStatus:
    overall_compliant: bool
    consent_coverage: float  # 0.0 - 1.0
    localization_compliant: bool
    pii_masking_rate: float  # 0.0 - 1.0
    breach_notifications_pending: int


class DPDPComplianceEngine:
    """Enforce DPDP Act 2023 requirements."""

    def __init__(self) -> None:
        self._consent_records: dict[str, list[ConsentRecord]] = {}
        self._processing_register: list[dict[str, Any]] = []
        self._breach_queue: list[dict[str, Any]] = []
        self._data_retention_days: int = 365
        self._localization_required: bool = True
        self._pii_actions_total: int = 0
        self._pii_actions_masked: int = 0

    def record_consent(self, record: ConsentRecord) -> None:
        self._consent_records.setdefault(record.data_principal_id, []).append(record)

    def check_consent(self, data_principal_id: str, purpose: str) -> bool:
        records = self._consent_records.get(data_principal_id, [])
        now = datetime.utcnow()
        for r in records:
            if r.purpose == purpose and r.granted:
                if r.expires_at and r.expires_at < now:
                    continue
                return True
        return False

    def record_processing(self, entry: dict[str, Any]) -> None:
        entry["timestamp"] = datetime.utcnow().isoformat()
        self._processing_register.append(entry)

    def report_breach(self, incident: dict[str, Any]) -> None:
        incident["reported_at"] = datetime.utcnow().isoformat()
        incident["status"] = "pending_notification"
        self._breach_queue.append(incident)

    def record_pii_action(self, masked: bool) -> None:
        self._pii_actions_total += 1
        if masked:
            self._pii_actions_masked += 1

    def get_status(self) -> DPDPStatus:
        total_principals = len(self._consent_records)
        consented = sum(
            1 for records in self._consent_records.values()
            if any(r.granted for r in records)
        )
        coverage = consented / max(total_principals, 1)
        masking_rate = self._pii_actions_masked / max(self._pii_actions_total, 1)
        pending = sum(1 for b in self._breach_queue if b.get("status") == "pending_notification")

        return DPDPStatus(
            overall_compliant=coverage >= 0.9 and masking_rate >= 0.95,
            consent_coverage=coverage,
            localization_compliant=self._localization_required,
            pii_masking_rate=masking_rate,
            breach_notifications_pending=pending,
        )
