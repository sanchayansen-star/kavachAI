"""CERT-In reporting — format incident data for Indian CERT submission."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class CERTInReport:
    incident_id: str
    report_type: str  # "cyber_security_incident"
    severity: str
    description: str
    affected_systems: list[str]
    timeline: list[dict[str, str]]
    evidence_hash: str
    generated_at: str


class CERTInReporter:
    """Format incident data for CERT-In submission."""

    def generate_report(
        self,
        incident_id: str,
        severity: str,
        description: str,
        audit_entries: list[dict[str, Any]],
        kill_chain: dict[str, Any] | None = None,
    ) -> CERTInReport:
        timeline = []
        affected = set()

        for entry in audit_entries:
            timeline.append({
                "timestamp": entry.get("timestamp", ""),
                "action": entry.get("action_type", ""),
                "verdict": entry.get("action_verdict", ""),
                "threat_score": str(entry.get("threat_score", 0)),
            })
            affected.add(entry.get("action_type", "unknown"))

        if kill_chain:
            for stage in kill_chain.get("stages", []):
                timeline.append({
                    "timestamp": stage.get("timestamp", ""),
                    "action": f"kill_chain_stage_{stage.get('stage_number', 0)}",
                    "verdict": stage.get("category", ""),
                    "threat_score": str(stage.get("threat_score", 0)),
                })

        # Evidence hash for tamper detection
        evidence_payload = json.dumps({"entries": audit_entries, "kill_chain": kill_chain}, sort_keys=True)
        evidence_hash = hashlib.sha256(evidence_payload.encode()).hexdigest()

        return CERTInReport(
            incident_id=incident_id,
            report_type="cyber_security_incident",
            severity=severity,
            description=description,
            affected_systems=sorted(affected),
            timeline=sorted(timeline, key=lambda t: t.get("timestamp", "")),
            evidence_hash=evidence_hash,
            generated_at=datetime.utcnow().isoformat(),
        )

    def format_for_submission(self, report: CERTInReport) -> dict[str, Any]:
        """Format report as structured JSON for CERT-In submission."""
        return {
            "report_format": "CERT-In-v1",
            "incident_id": report.incident_id,
            "type": report.report_type,
            "severity": report.severity,
            "description": report.description,
            "affected_systems": report.affected_systems,
            "timeline": report.timeline,
            "evidence": {
                "hash": report.evidence_hash,
                "algorithm": "SHA-256",
            },
            "generated_at": report.generated_at,
            "reporting_entity": "KavachAI Safety Firewall",
        }
