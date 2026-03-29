"""India AI Governance — Seven Sutras compliance mapping."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SevenSutrasScore:
    trust: int  # 0-100
    people_first: int
    innovation: int
    fairness: int
    accountability: int
    understandable: int
    safety: int

    def to_dict(self) -> dict[str, int]:
        return {
            "trust": self.trust,
            "people_first": self.people_first,
            "innovation": self.innovation,
            "fairness": self.fairness,
            "accountability": self.accountability,
            "understandable": self.understandable,
            "safety": self.safety,
        }


class SevenSutrasMapper:
    """Map KavachAI capabilities to India AI Seven Sutras principles."""

    def compute_scores(
        self,
        has_audit_trail: bool = True,
        has_pii_masking: bool = True,
        has_ethics_engine: bool = True,
        has_explainability: bool = False,
        has_threat_detection: bool = True,
        has_dpdp_compliance: bool = True,
        has_grounding: bool = False,
    ) -> SevenSutrasScore:
        # Trust: audit trail + cryptographic integrity
        trust = 90 if has_audit_trail else 30

        # People First: PII masking + DPDP compliance
        people_first = 0
        if has_pii_masking:
            people_first += 50
        if has_dpdp_compliance:
            people_first += 40

        # Innovation: grounding + advanced features
        innovation = 60 if has_grounding else 40

        # Fairness: ethics engine (bias detection)
        fairness = 85 if has_ethics_engine else 20

        # Accountability: audit trail + explainability
        accountability = 0
        if has_audit_trail:
            accountability += 50
        if has_explainability:
            accountability += 40
        else:
            accountability += 20

        # Understandable: explainability + decision explanations
        understandable = 80 if has_explainability else 40

        # Safety: threat detection + policy engine
        safety = 95 if has_threat_detection else 30

        return SevenSutrasScore(
            trust=trust,
            people_first=people_first,
            innovation=innovation,
            fairness=fairness,
            accountability=accountability,
            understandable=understandable,
            safety=safety,
        )
