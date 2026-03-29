"""Compliance API routes — DPDP status, incident export/report."""

from __future__ import annotations

from fastapi import APIRouter

from kavachai.backend.compliance.dpdp_engine import DPDPComplianceEngine

router = APIRouter(prefix="/api/v1/compliance", tags=["compliance"])

# Singleton (will be replaced with DI)
dpdp_engine = DPDPComplianceEngine()


@router.get("/dpdp-status")
async def get_dpdp_status():
    status = dpdp_engine.get_status()
    return {
        "overall_status": "compliant" if status.overall_compliant else "non_compliant",
        "consent_coverage": status.consent_coverage,
        "localization_compliance": status.localization_compliant,
        "pii_masking_rate": status.pii_masking_rate,
        "breach_notifications_pending": status.breach_notifications_pending,
    }


from kavachai.backend.compliance.seven_sutras import SevenSutrasMapper

_sutras_mapper = SevenSutrasMapper()


@router.get("/seven-sutras")
async def get_seven_sutras():
    scores = _sutras_mapper.compute_scores(
        has_audit_trail=True,
        has_pii_masking=True,
        has_ethics_engine=True,
        has_explainability=False,
        has_threat_detection=True,
        has_dpdp_compliance=True,
        has_grounding=False,
    )
    return {"scores": scores.to_dict()}
