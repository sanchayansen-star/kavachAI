"""Formal policy verifier — consistency, completeness, conflict detection."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from typing import Any

from kavachai.backend.models.policy import PolicyAST, PolicyRule, VerificationCertificate


class VerificationResult:
    def __init__(self) -> None:
        self.consistent = True
        self.complete = True
        self.conflicts: list[str] = []
        self.warnings: list[str] = []
        self.coverage: dict[str, bool] = {}


class FormalPolicyVerifier:
    """Offline verification of DSL policies."""

    def verify(self, policy: PolicyAST, known_tools: list[str] | None = None) -> VerificationCertificate:
        result = VerificationResult()

        self._check_consistency(policy, result)
        if known_tools:
            self._check_completeness(policy, known_tools, result)

        policy_hash = hashlib.sha256(policy.model_dump_json().encode()).hexdigest()

        return VerificationCertificate(
            policy_hash=policy_hash,
            verification_timestamp=datetime.utcnow(),
            properties_proven=self._proven_properties(result),
            consistent=result.consistent,
            complete=result.complete,
            conflicts=result.conflicts,
        )

    def _check_consistency(self, policy: PolicyAST, result: VerificationResult) -> None:
        """Check for conflicting rules — same trigger with contradictory enforcement."""
        trigger_map: dict[str, list[PolicyRule]] = {}

        for rule in policy.rules:
            trigger_key = self._trigger_key(rule.trigger)
            trigger_map.setdefault(trigger_key, []).append(rule)

        for key, rules in trigger_map.items():
            if len(rules) < 2:
                continue
            actions = {r.enforcement.get("action") for r in rules}
            # Conflict: same trigger has both "allow" and "block"
            if "allow" in actions and ("block" in actions or "quarantine" in actions):
                ids = [r.rule_id for r in rules]
                result.consistent = False
                result.conflicts.append(
                    f"Conflicting rules on trigger '{key}': {ids} have both allow and block/quarantine"
                )

    def _check_completeness(self, policy: PolicyAST, known_tools: list[str], result: VerificationResult) -> None:
        """Check if all known tools are covered by at least one rule."""
        covered_patterns: list[str] = []
        for rule in policy.rules:
            trigger = rule.trigger
            if trigger.get("type") == "tool_call":
                covered_patterns.extend(trigger.get("pattern", []))
            elif trigger.get("type") == "temporal":
                inner = trigger.get("inner", {})
                if inner.get("type") == "tool_call":
                    covered_patterns.extend(inner.get("pattern", []))

        has_wildcard = "*" in covered_patterns

        for tool in known_tools:
            import fnmatch
            covered = has_wildcard or any(fnmatch.fnmatch(tool, p) for p in covered_patterns)
            result.coverage[tool] = covered
            if not covered:
                result.complete = False
                result.warnings.append(f"Tool '{tool}' not covered by any policy rule")

    @staticmethod
    def _trigger_key(trigger: dict[str, Any]) -> str:
        ttype = trigger.get("type", "")
        if ttype == "tool_call":
            return f"tool_call:{','.join(sorted(trigger.get('pattern', [])))}"
        if ttype == "temporal":
            inner = trigger.get("inner", {})
            return f"{trigger.get('operator', '')}:{FormalPolicyVerifier._trigger_key(inner)}"
        return json.dumps(trigger, sort_keys=True)

    @staticmethod
    def _proven_properties(result: VerificationResult) -> list[str]:
        props = []
        if result.consistent:
            props.append("no_conflicting_rules")
        if result.complete:
            props.append("all_tools_covered")
        return props
