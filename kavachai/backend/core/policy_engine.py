"""Policy engine — evaluates ActionRequests against compiled PolicyASTs."""

from __future__ import annotations

import fnmatch
import re
import time
from datetime import datetime, timedelta
from typing import Any

from kavachai.backend.models.action import ActionRequest, VerdictType
from kavachai.backend.models.policy import PolicyAST, PolicyRule


class PolicyMatch:
    """Result of evaluating a single rule against an action."""

    def __init__(self, rule_id: str, matched: bool, verdict: VerdictType, reason: str = ""):
        self.rule_id = rule_id
        self.matched = matched
        self.verdict = verdict
        self.reason = reason


class PolicyEngine:
    """Load compiled PolicyASTs and evaluate ActionRequests against them.

    Maintains per-session action history for temporal constraint enforcement.
    Target: single rule evaluation within 10ms.
    """

    def __init__(self) -> None:
        self._policies: dict[str, PolicyAST] = {}
        # session_id -> list of (tool_name, timestamp)
        self._session_history: dict[str, list[tuple[str, datetime]]] = {}

    # ── Policy management ──

    def load_policy(self, policy: PolicyAST) -> None:
        self._policies[policy.policy_id] = policy

    def remove_policy(self, policy_id: str) -> None:
        self._policies.pop(policy_id, None)

    def get_policies(self) -> list[PolicyAST]:
        return list(self._policies.values())

    # ── Evaluation ──

    def evaluate(self, request: ActionRequest, agent_context: dict[str, Any] | None = None) -> list[PolicyMatch]:
        """Evaluate an ActionRequest against all loaded policies.

        Returns a list of PolicyMatch for every rule that matched.
        """
        ctx = agent_context or {}
        results: list[PolicyMatch] = []

        # Record action in session history
        history = self._session_history.setdefault(request.session_id, [])
        history.append((request.tool_name, request.timestamp))

        for policy in self._policies.values():
            for rule in policy.rules:
                match = self._evaluate_rule(rule, request, ctx, history)
                if match.matched:
                    results.append(match)

        return results

    def _evaluate_rule(
        self,
        rule: PolicyRule,
        request: ActionRequest,
        ctx: dict[str, Any],
        history: list[tuple[str, datetime]],
    ) -> PolicyMatch:
        trigger_hit = self._check_trigger(rule.trigger, request, history)
        if not trigger_hit:
            return PolicyMatch(rule.rule_id, False, VerdictType.ALLOW)

        predicate_hit = self._check_predicate(rule.predicate, request, ctx, history)
        if not predicate_hit:
            return PolicyMatch(rule.rule_id, False, VerdictType.ALLOW)

        verdict = _action_to_verdict(rule.enforcement.get("action", "block"))
        return PolicyMatch(
            rule.rule_id,
            True,
            verdict,
            reason=f"Rule {rule.rule_id} matched: {rule.enforcement}",
        )

    # ── Trigger matching ──

    def _check_trigger(
        self,
        trigger: dict[str, Any],
        request: ActionRequest,
        history: list[tuple[str, datetime]],
    ) -> bool:
        ttype = trigger.get("type")

        if ttype == "tool_call":
            return self._match_tool_pattern(trigger["pattern"], request.tool_name)

        if ttype == "state":
            # State triggers are evaluated by the DFA engine externally
            return False

        if ttype == "temporal":
            op = trigger.get("operator", "always")
            inner = trigger.get("inner", {})
            if op == "always":
                # "always(tool_call(*))" means this applies to every tool call
                return self._check_trigger(inner, request, history)
            if op == "eventually":
                return self._check_trigger(inner, request, history)
            # next / until — simplified: treat as current trigger
            return self._check_trigger(inner, request, history)

        return False

    @staticmethod
    def _match_tool_pattern(patterns: list[str], tool_name: str) -> bool:
        for pat in patterns:
            if pat == "*" or fnmatch.fnmatch(tool_name, pat):
                return True
        return False

    # ── Predicate evaluation ──

    def _check_predicate(
        self,
        pred: dict[str, Any],
        request: ActionRequest,
        ctx: dict[str, Any],
        history: list[tuple[str, datetime]],
    ) -> bool:
        ptype = pred.get("type")

        if ptype == "comparison":
            return self._eval_comparison(pred, request, ctx)

        if ptype == "and":
            return all(self._check_predicate(op, request, ctx, history) for op in pred["operands"])

        if ptype == "or":
            return any(self._check_predicate(op, request, ctx, history) for op in pred["operands"])

        if ptype == "temporal_pred":
            return self._eval_temporal_pred(pred, request, history)

        if ptype == "flow":
            return self._eval_flow_pred(pred, request, ctx)

        if ptype == "contains_pii":
            # PII detection is handled by the PII masker stage; always true here as a flag
            return True

        return False

    def _eval_comparison(
        self, pred: dict[str, Any], request: ActionRequest, ctx: dict[str, Any]
    ) -> bool:
        field_path: str = pred["field"]
        op: str = pred["op"]
        expected = pred["value"]

        actual = self._resolve_field(field_path, request, ctx)
        if actual is None:
            return False

        try:
            return _compare(actual, op, expected)
        except (TypeError, ValueError):
            return False

    def _eval_temporal_pred(
        self,
        pred: dict[str, Any],
        request: ActionRequest,
        history: list[tuple[str, datetime]],
    ) -> bool:
        dur = pred.get("duration", {})
        seconds = _duration_to_seconds(dur)
        trigger = pred.get("trigger", {})

        cutoff = request.timestamp - timedelta(seconds=seconds)
        for tool_name, ts in reversed(history):
            if ts < cutoff:
                break
            if trigger.get("type") == "tool_call" and self._match_tool_pattern(
                trigger["pattern"], tool_name
            ):
                return True
        return False

    @staticmethod
    def _eval_flow_pred(pred: dict[str, Any], request: ActionRequest, ctx: dict[str, Any]) -> bool:
        """Check if data from source reaches destination.

        Uses cumulative_effects from session context if available.
        """
        source = pred.get("source", "")
        destination = pred.get("destination", "")
        data_flows = ctx.get("cumulative_effects", {}).get("data_flows", [])
        for flow in data_flows:
            if source in flow.get("source", "") and destination in flow.get("destination", ""):
                return True
        # Heuristic: if tool is an external-facing tool, assume data flow
        external_tools = {"send_email", "external_api", "webhook", "http_request"}
        if request.tool_name in external_tools and destination == "external":
            return True
        return False

    @staticmethod
    def _resolve_field(field_path: str, request: ActionRequest, ctx: dict[str, Any]) -> Any:
        """Resolve a dotted field path against the request and agent context."""
        parts = field_path.split(".")
        root = parts[0]

        if root == "action":
            obj: Any = {"params": request.parameters, "tool_name": request.tool_name}
            for p in parts[1:]:
                if isinstance(obj, dict):
                    obj = obj.get(p)
                else:
                    return None
            return obj

        if root == "agent":
            obj = ctx.get("agent", {})
            for p in parts[1:]:
                if isinstance(obj, dict):
                    obj = obj.get(p)
                else:
                    return None
            return obj

        # Fallback: look in context
        obj = ctx
        for p in parts:
            if isinstance(obj, dict):
                obj = obj.get(p)
            else:
                return None
        return obj


# ── Helpers ──

_VERDICT_MAP = {
    "allow": VerdictType.ALLOW,
    "block": VerdictType.BLOCK,
    "flag": VerdictType.FLAG,
    "escalate": VerdictType.ESCALATE,
    "quarantine": VerdictType.QUARANTINE,
}


def _action_to_verdict(action: str) -> VerdictType:
    return _VERDICT_MAP.get(action, VerdictType.BLOCK)


def _compare(actual: Any, op: str, expected: Any) -> bool:
    # Coerce types for numeric comparisons
    if isinstance(expected, (int, float)) and isinstance(actual, str):
        try:
            actual = float(actual)
        except ValueError:
            return False
    if isinstance(actual, (int, float)) and isinstance(expected, str):
        try:
            expected = float(expected)
        except ValueError:
            return False

    if op == ">":
        return actual > expected
    if op == ">=":
        return actual >= expected
    if op == "<":
        return actual < expected
    if op == "<=":
        return actual <= expected
    if op == "==":
        return actual == expected
    if op == "!=":
        return actual != expected
    return False


def _duration_to_seconds(dur: dict[str, Any]) -> float:
    val = dur.get("value", 0)
    unit = dur.get("unit", "s")
    multipliers = {"ms": 0.001, "s": 1, "m": 60, "h": 3600}
    return val * multipliers.get(unit, 1)
