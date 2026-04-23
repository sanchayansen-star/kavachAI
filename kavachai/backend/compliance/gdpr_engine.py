"""GDPR Compliance Engine — EU General Data Protection Regulation.

Provides lawful basis tracking, right to erasure, data portability,
72-hour breach notification, DPIA status, and cross-border transfer controls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional


class LawfulBasis(str, Enum):
    """GDPR Article 6 — lawful bases for processing personal data."""

    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTEREST = "vital_interest"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTEREST = "legitimate_interest"


class TransferMechanism(str, Enum):
    """Mechanisms for lawful cross-border data transfers outside the EU/EEA."""

    ADEQUACY_DECISION = "adequacy_decision"
    STANDARD_CONTRACTUAL_CLAUSES = "scc"
    BINDING_CORPORATE_RULES = "bcr"
    EXPLICIT_CONSENT = "explicit_consent"
    NONE = "none"


class DPIAStatus(str, Enum):
    """Data Protection Impact Assessment status."""

    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REQUIRES_CONSULTATION = "requires_consultation"


@dataclass
class ErasureRequest:
    """Tracks a GDPR Article 17 right-to-erasure request."""

    request_id: str
    data_subject_id: str
    requested_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending | in_progress | completed | denied
    denial_reason: Optional[str] = None


@dataclass
class BreachRecord:
    """Tracks a personal data breach for 72-hour notification compliance."""

    breach_id: str
    detected_at: datetime
    description: str
    affected_data_subjects: int = 0
    notified_authority_at: Optional[datetime] = None
    notified_subjects_at: Optional[datetime] = None
    severity: str = "low"  # low | medium | high | critical

    @property
    def notification_deadline(self) -> datetime:
        """72 hours from detection per GDPR Article 33."""
        return self.detected_at + timedelta(hours=72)

    @property
    def hours_remaining(self) -> float:
        """Hours remaining until the 72-hour notification deadline."""
        now = datetime.now(timezone.utc)
        remaining = (self.notification_deadline - now).total_seconds() / 3600
        return max(0.0, remaining)

    @property
    def is_overdue(self) -> bool:
        return self.hours_remaining <= 0 and self.notified_authority_at is None


@dataclass
class CrossBorderTransfer:
    """Tracks a cross-border data transfer outside the EU/EEA."""

    transfer_id: str
    destination_country: str
    mechanism: TransferMechanism
    is_adequate: bool = False
    last_reviewed: Optional[datetime] = None


@dataclass
class GDPRStatus:
    """Overall GDPR compliance status snapshot."""

    overall_compliant: bool = True
    lawful_basis_coverage: float = 0.0
    processing_activities_with_basis: int = 0
    processing_activities_total: int = 0
    erasure_requests_pending: int = 0
    erasure_requests_completed: int = 0
    data_portability_supported: bool = True
    breach_notifications_pending: int = 0
    breach_notifications_overdue: int = 0
    dpia_status: str = "not_required"
    cross_border_transfers_compliant: int = 0
    cross_border_transfers_total: int = 0
    dpo_appointed: bool = False
    dpo_contact: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "overall_compliant": self.overall_compliant,
            "lawful_basis_coverage": self.lawful_basis_coverage,
            "processing_activities_with_basis": self.processing_activities_with_basis,
            "processing_activities_total": self.processing_activities_total,
            "erasure_requests_pending": self.erasure_requests_pending,
            "erasure_requests_completed": self.erasure_requests_completed,
            "data_portability_supported": self.data_portability_supported,
            "breach_notifications_pending": self.breach_notifications_pending,
            "breach_notifications_overdue": self.breach_notifications_overdue,
            "dpia_status": self.dpia_status,
            "cross_border_transfers_compliant": self.cross_border_transfers_compliant,
            "cross_border_transfers_total": self.cross_border_transfers_total,
            "dpo_appointed": self.dpo_appointed,
            "dpo_contact": self.dpo_contact,
        }


class GDPRComplianceEngine:
    """GDPR compliance engine for EU data protection requirements.

    Tracks lawful basis for processing, right to erasure requests,
    data portability, breach notifications, DPIAs, and cross-border transfers.
    Tenants can enable this engine when they operate under EU jurisdiction.
    """

    def __init__(self) -> None:
        self._lawful_bases: dict[str, LawfulBasis] = {}
        self._erasure_requests: list[ErasureRequest] = []
        self._breaches: list[BreachRecord] = []
        self._cross_border_transfers: list[CrossBorderTransfer] = []
        self._dpia_status: DPIAStatus = DPIAStatus.NOT_REQUIRED
        self._dpo_appointed: bool = False
        self._dpo_contact: Optional[str] = None

    # --- Lawful Basis Tracking ---

    def register_lawful_basis(
        self, processing_activity: str, basis: LawfulBasis
    ) -> None:
        """Register the lawful basis for a processing activity (Article 6)."""
        self._lawful_bases[processing_activity] = basis

    def get_lawful_basis(self, processing_activity: str) -> Optional[LawfulBasis]:
        """Get the registered lawful basis for a processing activity."""
        return self._lawful_bases.get(processing_activity)

    # --- Right to Erasure ---

    def submit_erasure_request(
        self, request_id: str, data_subject_id: str
    ) -> ErasureRequest:
        """Submit a right-to-erasure (right to be forgotten) request."""
        req = ErasureRequest(
            request_id=request_id,
            data_subject_id=data_subject_id,
            requested_at=datetime.now(timezone.utc),
        )
        self._erasure_requests.append(req)
        return req

    def complete_erasure_request(self, request_id: str) -> None:
        """Mark an erasure request as completed."""
        for req in self._erasure_requests:
            if req.request_id == request_id:
                req.status = "completed"
                req.completed_at = datetime.now(timezone.utc)
                return

    # --- Breach Notification ---

    def report_breach(
        self,
        breach_id: str,
        description: str,
        affected_count: int = 0,
        severity: str = "medium",
    ) -> BreachRecord:
        """Report a personal data breach. Starts the 72-hour notification clock."""
        breach = BreachRecord(
            breach_id=breach_id,
            detected_at=datetime.now(timezone.utc),
            description=description,
            affected_data_subjects=affected_count,
            severity=severity,
        )
        self._breaches.append(breach)
        return breach

    def notify_authority(self, breach_id: str) -> None:
        """Record that the supervisory authority has been notified."""
        for b in self._breaches:
            if b.breach_id == breach_id:
                b.notified_authority_at = datetime.now(timezone.utc)
                return

    # --- Cross-Border Transfers ---

    def register_transfer(
        self,
        transfer_id: str,
        destination_country: str,
        mechanism: TransferMechanism,
        is_adequate: bool = False,
    ) -> CrossBorderTransfer:
        """Register a cross-border data transfer with its legal mechanism."""
        transfer = CrossBorderTransfer(
            transfer_id=transfer_id,
            destination_country=destination_country,
            mechanism=mechanism,
            is_adequate=is_adequate,
            last_reviewed=datetime.now(timezone.utc),
        )
        self._cross_border_transfers.append(transfer)
        return transfer

    # --- DPIA ---

    def set_dpia_status(self, status: DPIAStatus) -> None:
        """Update the Data Protection Impact Assessment status."""
        self._dpia_status = status

    # --- DPO ---

    def appoint_dpo(self, contact: str) -> None:
        """Record the appointment of a Data Protection Officer."""
        self._dpo_appointed = True
        self._dpo_contact = contact

    # --- Status ---

    def get_status(self) -> GDPRStatus:
        """Get the current GDPR compliance status snapshot."""
        total_activities = max(len(self._lawful_bases), 1)
        activities_with_basis = sum(
            1 for b in self._lawful_bases.values() if b is not None
        )

        pending_erasure = sum(
            1 for r in self._erasure_requests if r.status == "pending"
        )
        completed_erasure = sum(
            1 for r in self._erasure_requests if r.status == "completed"
        )

        pending_breach = sum(
            1
            for b in self._breaches
            if b.notified_authority_at is None and not b.is_overdue
        )
        overdue_breach = sum(1 for b in self._breaches if b.is_overdue)

        compliant_transfers = sum(
            1
            for t in self._cross_border_transfers
            if t.mechanism != TransferMechanism.NONE
        )

        overall = (
            overdue_breach == 0
            and activities_with_basis == total_activities
            and (
                len(self._cross_border_transfers) == 0
                or compliant_transfers == len(self._cross_border_transfers)
            )
        )

        return GDPRStatus(
            overall_compliant=overall,
            lawful_basis_coverage=activities_with_basis / total_activities,
            processing_activities_with_basis=activities_with_basis,
            processing_activities_total=total_activities,
            erasure_requests_pending=pending_erasure,
            erasure_requests_completed=completed_erasure,
            data_portability_supported=True,
            breach_notifications_pending=pending_breach,
            breach_notifications_overdue=overdue_breach,
            dpia_status=self._dpia_status.value,
            cross_border_transfers_compliant=compliant_transfers,
            cross_border_transfers_total=len(self._cross_border_transfers),
            dpo_appointed=self._dpo_appointed,
            dpo_contact=self._dpo_contact,
        )
