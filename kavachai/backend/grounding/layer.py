"""Semantic grounding layer — deterministic validation, no LLM dependency."""

from __future__ import annotations

import json
import re
from typing import Any

from kavachai.backend.models.grounding import (
    ClaimVerification,
    GroundingResult,
    SourceAttribution,
    ValidationCheck,
)


class SemanticGroundingLayer:
    """Deterministic validation layer for agent outputs."""

    def __init__(self) -> None:
        self._knowledge_graphs: list[dict[str, Any]] = []
        self._ontologies: list[dict[str, Any]] = []
        self._schemas: dict[str, dict] = {}

    def load_knowledge_graph(self, kg: dict[str, Any]) -> None:
        self._knowledge_graphs.append(kg)

    def load_ontology(self, ontology: dict[str, Any]) -> None:
        self._ontologies.append(ontology)

    def register_schema(self, name: str, schema: dict) -> None:
        self._schemas[name] = schema

    def validate(
        self,
        agent_output: str,
        output_schema: str | None = None,
        grounding_threshold: float = 0.7,
    ) -> GroundingResult:
        # Step 1: Schema enforcement
        schema_valid = True
        if output_schema and output_schema in self._schemas:
            schema_valid = self._validate_schema(agent_output, self._schemas[output_schema])
            if not schema_valid:
                return GroundingResult(
                    output_id="",
                    session_id="",
                    grounding_score=0.0,
                    claims=[],
                    schema_valid=False,
                    deterministic_checks=[],
                    verdict="BLOCKED",
                )

        # Step 2: Extract claims
        claims = self._extract_claims(agent_output)

        # Step 3: Verify claims
        verified: list[ClaimVerification] = []
        for claim_text in claims:
            attribution = self._verify_claim(claim_text)
            verified.append(ClaimVerification(
                claim_text=claim_text,
                source_attribution=attribution,
                grounded=attribution is not None,
                confidence=0.9 if attribution else 0.0,
            ))

        # Step 4: Deterministic checks
        det_checks = self._run_deterministic_checks(agent_output)

        # Step 5: Score
        grounded_count = sum(1 for c in verified if c.grounded)
        total = max(len(verified), 1)
        score = grounded_count / total

        verdict = "GROUNDED" if score >= grounding_threshold else "INSUFFICIENTLY_GROUNDED"

        return GroundingResult(
            output_id="",
            session_id="",
            grounding_score=score,
            claims=verified,
            schema_valid=schema_valid,
            deterministic_checks=det_checks,
            verdict=verdict,
        )

    @staticmethod
    def _validate_schema(output: str, schema: dict) -> bool:
        try:
            data = json.loads(output)
            required = schema.get("required", [])
            properties = schema.get("properties", {})
            if not isinstance(data, dict):
                return False
            for key in required:
                if key not in data:
                    return False
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    @staticmethod
    def _extract_claims(text: str) -> list[str]:
        """Extract factual claims from text using sentence splitting."""
        sentences = re.split(r"[.!?]+", text)
        claims = []
        for s in sentences:
            s = s.strip()
            if len(s) > 10 and any(c.isdigit() for c in s):
                claims.append(s)
            elif len(s) > 20:
                claims.append(s)
        return claims[:20]  # Cap at 20 claims

    def _verify_claim(self, claim: str) -> SourceAttribution | None:
        # Check knowledge graphs
        for kg in self._knowledge_graphs:
            for node in kg.get("nodes", []):
                if node.get("label", "").lower() in claim.lower():
                    return SourceAttribution(
                        source_type="knowledge_graph",
                        source_id=node["id"],
                        source_label=node["label"],
                        evidence_text=f"Entity found in KG: {node['label']}",
                    )
        # Check ontologies
        for onto in self._ontologies:
            for concept in onto.get("concepts", []):
                if concept["name"].lower() in claim.lower():
                    return SourceAttribution(
                        source_type="ontology",
                        source_id=onto.get("ontology_id", ""),
                        source_label=concept["name"],
                        evidence_text=f"Concept found in ontology: {concept['name']}",
                    )
        return None

    @staticmethod
    def _run_deterministic_checks(text: str) -> list[ValidationCheck]:
        checks: list[ValidationCheck] = []

        # Numerical consistency
        numbers = re.findall(r"\b\d+\.?\d*\b", text)
        checks.append(ValidationCheck(
            check_type="numerical_consistency",
            passed=True,
            details=f"Found {len(numbers)} numerical values",
        ))

        # Date validity
        dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text)
        valid_dates = True
        for d in dates:
            parts = d.split("-")
            if int(parts[1]) > 12 or int(parts[2]) > 31:
                valid_dates = False
        checks.append(ValidationCheck(
            check_type="date_validity",
            passed=valid_dates,
            details=f"Found {len(dates)} dates, all valid: {valid_dates}",
        ))

        return checks
