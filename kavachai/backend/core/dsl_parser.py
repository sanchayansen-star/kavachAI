"""KavachAI DSL parser using Lark — Trigger-Predicate-Enforcement pattern with LTL operators."""

import uuid
from typing import Any

from lark import Lark, Transformer, v_args, UnexpectedInput

from kavachai.backend.models.policy import PolicyAST, PolicyRule

# ---------- PEG-style grammar (Lark EBNF) ----------

KAVACHAI_GRAMMAR = r"""
start: header import_stmt* (rule_block | workflow_block | template_block | ethics_rule)+ 

// ── Header ──
header: "policy" IDENT version? description?
version: "version" ESCAPED_STRING
description: "description" ESCAPED_STRING

// ── Imports ──
import_stmt: "import" IDENT ("from" ESCAPED_STRING)?

// ── Rule block ──
rule_block: "rule" IDENT "{" trigger predicate enforcement "}"

// ── Triggers ──
trigger: "when" trigger_expr
trigger_expr: tool_call_trigger
            | state_trigger
            | temporal_trigger
tool_call_trigger: "tool_call" "(" tool_pattern ")"
state_trigger: "state" "(" state_expr ")"
temporal_trigger: LTL_OP "(" trigger_expr ")"
LTL_OP: "always" | "eventually" | "until" | "next"
tool_pattern: ESCAPED_STRING ("|" ESCAPED_STRING)*
state_expr: IDENT "==" ESCAPED_STRING

// ── Predicates ──
predicate: "check" predicate_expr
predicate_expr: or_expr
or_expr: and_expr ("or" and_expr)*
and_expr: atom_pred ("and" atom_pred)*
atom_pred: comparison
         | temporal_pred
         | flow_pred
         | contains_pii_pred
         | "(" predicate_expr ")"
comparison: field_ref COMP_OP value
COMP_OP: ">=" | "<=" | "!=" | "==" | ">" | "<"
field_ref: IDENT ("." IDENT)*
value: ESCAPED_STRING | NUMBER | BOOLEAN
BOOLEAN: "true" | "false"
temporal_pred: "within" duration "of" trigger_expr
duration: NUMBER DURATION_UNIT
DURATION_UNIT: "ms" | "s" | "m" | "h"
flow_pred: "data_from" ESCAPED_STRING "reaches" ESCAPED_STRING
contains_pii_pred: "output" "contains_pii" "(" tool_pattern ")"

// ── Enforcement ──
enforcement: "then" ACTION_TYPE severity?
ACTION_TYPE: "allow" | "block" | "flag" | "escalate" | "quarantine"
severity: "severity" SEVERITY_LEVEL
SEVERITY_LEVEL: "low" | "medium" | "high" | "critical"

// ── Workflow / DFA ──
workflow_block: "workflow" IDENT "{" state_def+ transition+ "}"
state_def: "state" IDENT STATE_TYPE?
STATE_TYPE: "initial" | "accepting" | "dangerous"
transition: IDENT "->" IDENT "on" "tool_call" "(" tool_pattern ")" guard?
guard: "if" predicate_expr

// ── Parameterised templates ──
template_block: "template" IDENT "(" param_list ")" "{" rule_block+ "}"
param_list: param ("," param)*
param: IDENT ":" type_name ("=" value)?
type_name: IDENT

// ── Ethics constructs ──
ethics_rule: "ensure" ETHICS_DIM "in" IDENT "for" ethics_target
ETHICS_DIM: "fairness" | "safety" | "transparency" | "accountability"
ethics_target: "all" IDENT | IDENT

// ── Terminals ──
IDENT: /[a-zA-Z_][a-zA-Z0-9_*]*/
%import common.ESCAPED_STRING
%import common.NUMBER
%import common.WS
%import common.SH_COMMENT
%ignore WS
%ignore SH_COMMENT
"""

_parser = Lark(KAVACHAI_GRAMMAR, parser="earley", propagate_positions=True)


# ---------- AST Transformer ----------

@v_args(inline=True)
class _ASTBuilder(Transformer):
    """Convert Lark parse tree into PolicyAST-compatible dicts."""

    # ── Header ──
    def header(self, name, *rest):
        return {"name": str(name), "version": "1.0", "description": ""}

    def version(self, v):
        return ("version", str(v).strip('"'))

    def description(self, d):
        return ("description", str(d).strip('"'))

    # ── Import ──
    def import_stmt(self, name, *rest):
        src = str(rest[0]).strip('"') if rest else None
        return {"import": str(name), "from": src}

    # ── Rule ──
    def rule_block(self, name, trigger, predicate, enforcement):
        return {
            "type": "rule",
            "rule_id": str(name),
            "trigger": trigger,
            "predicate": predicate,
            "enforcement": enforcement,
        }

    # ── Triggers ──
    def trigger(self, expr):
        return expr

    def trigger_expr(self, inner):
        return inner

    def tool_call_trigger(self, pattern):
        return {"type": "tool_call", "pattern": pattern}

    def state_trigger(self, expr):
        return {"type": "state", "expr": expr}

    def temporal_trigger(self, op, inner):
        return {"type": "temporal", "operator": str(op), "inner": inner}

    def tool_pattern(self, *parts):
        return [str(p).strip('"') for p in parts]

    def state_expr(self, ident, val):
        return {"field": str(ident), "value": str(val).strip('"')}

    # ── Predicates ──
    def predicate(self, expr):
        return expr

    def predicate_expr(self, inner):
        return inner

    def or_expr(self, *args):
        if len(args) == 1:
            return args[0]
        return {"type": "or", "operands": list(args)}

    def and_expr(self, *args):
        if len(args) == 1:
            return args[0]
        return {"type": "and", "operands": list(args)}

    def atom_pred(self, inner):
        return inner

    def comparison(self, field, op, val):
        return {"type": "comparison", "field": field, "op": str(op), "value": val}

    def field_ref(self, *parts):
        return ".".join(str(p) for p in parts)

    def value(self, v):
        s = str(v)
        if s.startswith('"') and s.endswith('"'):
            return s.strip('"')
        if s in ("true", "false"):
            return s == "true"
        try:
            return int(s)
        except ValueError:
            return float(s)

    def temporal_pred(self, dur, trigger):
        return {"type": "temporal_pred", "duration": dur, "trigger": trigger}

    def duration(self, num, unit):
        return {"value": int(num), "unit": str(unit)}

    def flow_pred(self, src, dst):
        return {"type": "flow", "source": str(src).strip('"'), "destination": str(dst).strip('"')}

    def contains_pii_pred(self, pattern):
        return {"type": "contains_pii", "categories": pattern}

    # ── Enforcement ──
    def enforcement(self, act, sev=None):
        return {"action": str(act), "severity": str(sev) if sev else "medium"}

    def severity(self, *args):
        return str(args[0]) if args else "medium"

    # ── Workflow ──
    def workflow_block(self, name, *children):
        states = [c for c in children if isinstance(c, dict) and c.get("type") == "state_def"]
        transitions = [c for c in children if isinstance(c, dict) and c.get("type") == "transition"]
        return {
            "type": "workflow",
            "name": str(name),
            "states": states,
            "transitions": transitions,
        }

    def state_def(self, name, stype=None):
        return {"type": "state_def", "name": str(name), "state_type": str(stype) if stype else None}

    def transition(self, src, dst, pattern, guard=None):
        return {
            "type": "transition",
            "from": str(src),
            "to": str(dst),
            "tool_pattern": pattern,
            "guard": guard,
        }

    def guard(self, expr):
        return expr

    # ── Template ──
    def template_block(self, name, params, *rules):
        return {
            "type": "template",
            "name": str(name),
            "params": params,
            "rules": list(rules),
        }

    def param_list(self, *params):
        return list(params)

    def param(self, name, tname, *default):
        return {"name": str(name), "type": str(tname), "default": default[0] if default else None}

    def type_name(self, t):
        return str(t)

    # ── Ethics ──
    def ethics_rule(self, dimension, scope, target):
        return {
            "type": "ethics",
            "dimension": str(dimension),
            "scope": str(scope),
            "target": target,
        }

    def ethics_target(self, *parts):
        return " ".join(str(p) for p in parts)

    # ── Top-level ──
    def start(self, header, *children):
        return {"header": header, "children": list(children)}


_transformer = _ASTBuilder()


# ---------- Public API ----------

class DSLParseError(Exception):
    """Raised when DSL source cannot be parsed."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        self.line = line
        self.column = column
        super().__init__(message)


def parse_dsl(source: str) -> PolicyAST:
    """Parse KavachAI DSL source text into a PolicyAST.

    Raises DSLParseError with line/column on syntax errors.
    """
    try:
        tree = _parser.parse(source)
    except UnexpectedInput as exc:
        raise DSLParseError(str(exc), line=getattr(exc, "line", None), column=getattr(exc, "column", None)) from exc

    raw = _transformer.transform(tree)
    header = raw["header"]

    # Apply version/description overrides from header children
    for child in raw["children"]:
        if isinstance(child, tuple):
            if child[0] == "version":
                header["version"] = child[1]
            elif child[0] == "description":
                header["description"] = child[1]

    imports: list[str] = []
    rules: list[PolicyRule] = []
    workflows: list[dict[str, Any]] = []
    ethics_rules: list[dict[str, Any]] = []

    for child in raw["children"]:
        if isinstance(child, tuple):
            continue
        if not isinstance(child, dict):
            continue
        ctype = child.get("type")
        if ctype == "rule":
            rules.append(PolicyRule(
                rule_id=child["rule_id"],
                trigger=child["trigger"],
                predicate=child["predicate"],
                enforcement=child["enforcement"],
                severity=child["enforcement"].get("severity", "medium"),
            ))
        elif ctype == "workflow":
            workflows.append(child)
        elif ctype == "ethics":
            ethics_rules.append(child)
        elif ctype == "template":
            # Templates stored as-is for later expansion
            pass
        elif "import" in child:
            imports.append(child["import"])

    return PolicyAST(
        policy_id=str(uuid.uuid4()),
        name=header["name"],
        version=header["version"],
        description=header["description"],
        imports=imports,
        rules=rules,
        workflows=workflows,
        ethics_rules=ethics_rules,
    )
