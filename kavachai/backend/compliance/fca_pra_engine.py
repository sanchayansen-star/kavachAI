"""UK Financial Regulatory Compliance Engine — FCA, PRA, SM&CR, DORA, MiFID II.

Provides compliance tracking for UK financial services regulations
applicable to AI/ML systems in financial institutions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ConsumerDutyStatus(str, Enum):
    """FCA Consumer Duty compliance status."""

    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"


class ModelRiskTier(str, Enum):
    """PRA SS1/23 model risk tiering."""

    TIER_1 = "tier_1"  # High impact — requires full validation
    TIER_2 = "tier_2"  # Medium impact — requires periodic review
    TIER_3 = "tier_3"  # Low impact — requires documentation only


class ModelValidationStatus(str, Enum):
    """PRA SS1/23 model validation status."""

    NOT_VALIDATED = "not_validated"
    VALIDATION_IN_PROGRESS = "validation_in_progress"
    VALIDATED = "validated"
    VALIDATION_EXPIRED = "validation_expired"
    REQUIRES_REVALIDATION = "requires_revalidation"


class DORAComplianceLevel(str, Enum):
    """DORA ICT risk management compliance level."""

    FULL = "full"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class SMCRAccountability:
    """SM&CR — maps a Senior Manager to an AI system they are accountable for."""

    senior_manager_id: str
    senior_manager_name: str
    function_title: str  # e.g., "Chief Risk Officer", "Head of AI"
    ai_system_id: str
    ai_system_name: str
    accountability_scope: str  # Description of what they are accountable for
    appointed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_reviewed: Optional[datetime] = None


@dataclass
class MiFIDIIControls:
    """MiFID II algorithmic trading controls status."""

    algorithmic_trading_registered: bool = False
    kill_switch_enabled: bool = False
    pre_trade_risk_controls: bool = False
    post_trade_monitoring: bool = False
    best_execution_policy: bool = False
    transaction_reporting: bool = False
    last_reviewed: Optional[datetime] = None

    @property
    def compliant(self) -> bool:
        return all([
            self.algorithmic_trading_registered,
            self.kill_switch_enabled,
            self.pre_trade_risk_controls,
            self.post_trade_monitoring,
            self.best_execution_policy,
            self.transaction_reporting,
        ])

    def to_dict(self) -> dict:
        return {
            "algorithmic_trading_registered": self.algorithmic_trading_registered,
            "kill_switch_enabled": self.kill_switch_enabled,
            "pre_trade_risk_controls": self.pre_trade_risk_controls,
            "post_trade_monitoring": self.post_trade_monitoring,
            "best_execution_policy": self.best_execution_policy,
            "transaction_reporting": self.transaction_reporting,
            "compliant": self.compliant,
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
        }


@dataclass
class FinancialRegulatoryStatus:
    """Overall UK financial regulatory compliance status snapshot."""

    # FCA Consumer Duty
    consumer_duty_status: str = "under_review"
    consumer_duty_outcomes_monitored: bool = False
    treating_customers_fairly: bool = True
    operational_resilience_tested: bool = False

    # PRA SS1/23 Model Risk
    model_risk_tier: str = "tier_2"
    model_validation_status: str = "not_validated"
    model_inventory_complete: bool = False
    ongoing_monitoring_active: bool = False
    model_documentation_complete: bool = False

    # SM&CR
    smcr_accountability_mapped: bool = False
    senior_managers_assigned: int = 0
    ai_systems_covered: int = 0

    # DORA
    dora_ict_risk_status: str = "non_compliant"
    dora_incident_reporting_ready: bool = False
    dora_third_party_risk_assessed: bool = False

    # MiFID II
    mifid_ii_compliant: bool = False
    mifid_ii_controls: Optional[dict] = None

    # Overall
    overall_compliant: bool = False

    def to_dict(self) -> dict:
        return {
            "overall_compliant": self.overall_compliant,
            "fca_consumer_duty": {
                "status": self.consumer_duty_status,
                "outcomes_monitored": self.consumer_duty_outcomes_monitored,
                "treating_customers_fairly": self.treating_customers_fairly,
                "operational_resilience_tested": self.operational_resilience_tested,
            },
            "pra_ss1_23": {
                "model_risk_tier": self.model_risk_tier,
                "model_validation_status": self.model_validation_status,
                "model_inventory_complete": self.model_inventory_complete,
                "ongoing_monitoring_active": self.ongoing_monitoring_active,
                "model_documentation_complete": self.model_documentation_complete,
            },
            "smcr": {
                "accountability_mapped": self.smcr_accountability_mapped,
                "senior_managers_assigned": self.senior_managers_assigned,
                "ai_systems_covered": self.ai_systems_covered,
            },
            "dora": {
                "ict_risk_status": self.dora_ict_risk_status,
                "incident_reporting_ready": self.dora_incident_reporting_ready,
                "third_party_risk_assessed": self.dora_third_party_risk_assessed,
            },
            "mifid_ii": {
                "compliant": self.mifid_ii_compliant,
                "controls": self.mifid_ii_controls,
            },
        }


class FinancialRegulatoryEngine:
    """UK financial regulatory compliance engine.

    Tracks compliance with FCA Consumer Duty, PRA SS1/23 model risk management,
    SM&CR accountability, DORA ICT risk management, and MiFID II controls.
    Tenants can enable this engine when they operate under UK/EU financial jurisdiction.
    """

    def __init__(self) -> None:
        # FCA
        self._consumer_duty_status = ConsumerDutyStatus.UNDER_REVIEW
        self._outcomes_monitored = False
        self._treating_customers_fairly = True
        self._operational_resilience_tested = False

        # PRA SS1/23
        self._model_risk_tier = ModelRiskTier.TIER_2
        self._model_validation_status = ModelValidationStatus.NOT_VALIDATED
        self._model_inventory_complete = False
        self._ongoing_monitoring = False
        self._model_documentation = False

        # SM&CR
        self._accountability_map: list[SMCRAccountability] = []

        # DORA
        self._dora_level = DORAComplianceLevel.NON_COMPLIANT
        self._dora_incident_reporting = False
        self._dora_third_party_risk = False

        # MiFID II
        self._mifid_controls = MiFIDIIControls()

    # --- FCA Consumer Duty ---

    def set_consumer_duty_status(self, status: ConsumerDutyStatus) -> None:
        """Update FCA Consumer Duty compliance status."""
        self._consumer_duty_status = status

    def set_outcomes_monitored(self, monitored: bool) -> None:
        """Record whether customer outcomes are being monitored."""
        self._outcomes_monitored = monitored

    def set_operational_resilience_tested(self, tested: bool) -> None:
        """Record whether operational resilience has been tested."""
        self._operational_resilience_tested = tested

    # --- PRA SS1/23 ---

    def set_model_risk_tier(self, tier: ModelRiskTier) -> None:
        """Set the model risk tier per PRA SS1/23."""
        self._model_risk_tier = tier

    def set_model_validation_status(self, status: ModelValidationStatus) -> None:
        """Update model validation status."""
        self._model_validation_status = status

    def set_model_inventory_complete(self, complete: bool) -> None:
        """Record whether the model inventory is complete."""
        self._model_inventory_complete = complete

    def set_ongoing_monitoring(self, active: bool) -> None:
        """Record whether ongoing model monitoring is active."""
        self._ongoing_monitoring = active

    def set_model_documentation(self, complete: bool) -> None:
        """Record whether model documentation is complete."""
        self._model_documentation = complete

    # --- SM&CR ---

    def assign_accountability(
        self,
        senior_manager_id: str,
        senior_manager_name: str,
        function_title: str,
        ai_system_id: str,
        ai_system_name: str,
        accountability_scope: str,
    ) -> SMCRAccountability:
        """Map a Senior Manager to an AI system under SM&CR."""
        mapping = SMCRAccountability(
            senior_manager_id=senior_manager_id,
            senior_manager_name=senior_manager_name,
            function_title=function_title,
            ai_system_id=ai_system_id,
            ai_system_name=ai_system_name,
            accountability_scope=accountability_scope,
        )
        self._accountability_map.append(mapping)
        return mapping

    def get_accountability_map(self) -> list[SMCRAccountability]:
        """Get the full SM&CR accountability map."""
        return list(self._accountability_map)

    # --- DORA ---

    def set_dora_compliance(self, level: DORAComplianceLevel) -> None:
        """Set DORA ICT risk management compliance level."""
        self._dora_level = level

    def set_dora_incident_reporting(self, ready: bool) -> None:
        """Record whether DORA incident reporting is ready."""
        self._dora_incident_reporting = ready

    def set_dora_third_party_risk(self, assessed: bool) -> None:
        """Record whether third-party ICT risk has been assessed."""
        self._dora_third_party_risk = assessed

    # --- MiFID II ---

    def update_mifid_controls(self, **kwargs: bool) -> None:
        """Update MiFID II algorithmic trading controls.

        Accepts keyword arguments matching MiFIDIIControls fields:
        algorithmic_trading_registered, kill_switch_enabled,
        pre_trade_risk_controls, post_trade_monitoring,
        best_execution_policy, transaction_reporting.
        """
        for key, value in kwargs.items():
            if hasattr(self._mifid_controls, key):
                setattr(self._mifid_controls, key, value)
        self._mifid_controls.last_reviewed = datetime.now(timezone.utc)

    # --- Status ---

    def get_status(self) -> FinancialRegulatoryStatus:
        """Get the current financial regulatory compliance status snapshot."""
        unique_managers = len(
            {m.senior_manager_id for m in self._accountability_map}
        )
        unique_systems = len(
            {m.ai_system_id for m in self._accountability_map}
        )
        smcr_mapped = unique_systems > 0

        fca_ok = self._consumer_duty_status in (
            ConsumerDutyStatus.COMPLIANT,
            ConsumerDutyStatus.PARTIALLY_COMPLIANT,
        )
        pra_ok = self._model_validation_status == ModelValidationStatus.VALIDATED
        dora_ok = self._dora_level in (
            DORAComplianceLevel.FULL,
            DORAComplianceLevel.NOT_APPLICABLE,
        )

        overall = fca_ok and pra_ok and smcr_mapped

        return FinancialRegulatoryStatus(
            consumer_duty_status=self._consumer_duty_status.value,
            consumer_duty_outcomes_monitored=self._outcomes_monitored,
            treating_customers_fairly=self._treating_customers_fairly,
            operational_resilience_tested=self._operational_resilience_tested,
            model_risk_tier=self._model_risk_tier.value,
            model_validation_status=self._model_validation_status.value,
            model_inventory_complete=self._model_inventory_complete,
            ongoing_monitoring_active=self._ongoing_monitoring,
            model_documentation_complete=self._model_documentation,
            smcr_accountability_mapped=smcr_mapped,
            senior_managers_assigned=unique_managers,
            ai_systems_covered=unique_systems,
            dora_ict_risk_status=self._dora_level.value,
            dora_incident_reporting_ready=self._dora_incident_reporting,
            dora_third_party_risk_assessed=self._dora_third_party_risk,
            mifid_ii_compliant=self._mifid_controls.compliant,
            mifid_ii_controls=self._mifid_controls.to_dict(),
            overall_compliant=overall,
        )
