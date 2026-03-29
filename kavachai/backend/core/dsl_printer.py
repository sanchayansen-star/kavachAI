"""Serialize a PolicyAST back to valid KavachAI DSL source text."""

from __future__ import annotations

from typing import Any

from kavachai.backend.models.policy import PolicyAST, PolicyRule


def print_dsl(ast: PolicyAST) -> str:
    """Convert a PolicyAST into canonical KavachAI DSL source."""
    lines: list[str] = []

    # Header
    lines.append(f'policy {ast.name}')
    if ast.version:
        lines.append(f'version "{ast.version}"')
    if ast.description:
        lines.append(f'description "{ast.description}"')
    lines.append("")

    # Imports
    for imp in ast.imports:
        lines.append(f"import {imp}")
    if ast.imports:
        lines.append("")

    # Rules
    for rule in ast.rules:
        lines.extend(_print_rule(rule))
        lines.append("")

    # Workflows
    for wf in ast.workflows:
        lines.extend(_print_workflow(wf))
        lines.append("")

    # Ethics rules
    for er in ast.ethics_rules:
        lines.append(f'ensure {er["dimension"]} in {er["scope"]} for {er["target"]}')
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _print_rule(rule: PolicyRule) -> list[str]:
    lines = [f"rule {rule.rule_id} {{"]
    lines.append(f"  when {_print_trigger(rule.trigger)}")
    lines.append(f"  check {_print_predicate(rule.predicate)}")
    sev = f' severity {rule.severity}' if rule.severity != "medium" else ""
    lines.append(f"  then {rule.enforcement['action']}{sev}")
    lines.append("}")
    return lines


def _print_trigger(t: dict[str, Any]) -> str:
    ttype = t.get("type")
    if ttype == "tool_call":
        pats = " | ".join(f'"{p}"' for p in t["pattern"])
        return f"tool_call({pats})"
    if ttype == "state":
        expr = t["expr"]
        return f'state({expr["field"]} == "{expr["value"]}")'
    if ttype == "temporal":
        return f'{t["operator"]}({_print_trigger(t["inner"])})'
    return str(t)


def _print_predicate(p: dict[str, Any]) -> str:
    ptype = p.get("type")
    if ptype == "comparison":
        return f'{p["field"]} {p["op"]} {_print_value(p["value"])}'
    if ptype == "and":
        parts = [_print_predicate(op) for op in p["operands"]]
        return "\n    and ".join(parts)
    if ptype == "or":
        parts = [_print_predicate(op) for op in p["operands"]]
        return "\n    or ".join(parts)
    if ptype == "temporal_pred":
        dur = p["duration"]
        return f'within {dur["value"]}{dur["unit"]} of {_print_trigger(p["trigger"])}'
    if ptype == "flow":
        return f'data_from "{p["source"]}" reaches "{p["destination"]}"'
    if ptype == "contains_pii":
        cats = " | ".join(f'"{c}"' for c in p["categories"])
        return f"output contains_pii({cats})"
    return str(p)


def _print_value(v: Any) -> str:
    if isinstance(v, str):
        return f'"{v}"'
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def _print_workflow(wf: dict[str, Any]) -> list[str]:
    lines = [f'workflow {wf["name"]} {{']
    for s in wf.get("states", []):
        st = f' {s["state_type"]}' if s.get("state_type") else ""
        lines.append(f'  state {s["name"]}{st}')
    lines.append("")
    for tr in wf.get("transitions", []):
        pats = " | ".join(f'"{p}"' for p in tr["tool_pattern"])
        guard = ""
        if tr.get("guard"):
            guard = f" if {_print_predicate(tr['guard'])}"
        lines.append(f'  {tr["from"]} -> {tr["to"]} on tool_call({pats}){guard}')
    lines.append("}")
    return lines
