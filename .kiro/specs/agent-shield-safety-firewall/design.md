# Technical Design Document — KavachAI: Zero Trust Safety Firewall for Agentic AI

## Table of Contents

- [1. High-Level System Architecture](#1-high-level-system-architecture)
- [2. Data Models](#2-data-models)
  - [2.1 Agent Identity](#21-agent-identity)
  - [2.2 Capability Token](#22-capability-token)
  - [2.3 Action Request / Verdict](#23-action-request--verdict)
  - [2.4 Action Attestation](#24-action-attestation)
  - [2.5 Audit Entry (Hash Chain)](#25-audit-entry-hash-chain)
  - [2.6 Kill Chain](#26-kill-chain)
  - [2.7 Semantic Grounding Models](#27-semantic-grounding-models)
  - [2.8 LLM Evaluation Models](#28-llm-evaluation-models)
- [3. API Design](#3-api-design)
  - [3.1 Core Evaluation API](#31-core-evaluation-api)
  - [3.2 Session & Threat APIs](#32-session--threat-apis)
  - [3.3 Policy Management APIs](#33-policy-management-apis)
  - [3.4 Escalation APIs](#34-escalation-apis)
  - [3.5 LLM Gateway APIs](#35-llm-gateway-apis)
  - [3.6 LLM Evaluation APIs](#36-llm-evaluation-apis)
  - [3.7 Compliance & Reporting APIs](#37-compliance--reporting-apis)
  - [3.8 WebSocket — Real-Time Dashboard Feed](#38-websocket--real-time-dashboard-feed)
- [4. MCP Proxy Architecture](#4-mcp-proxy-architecture)
- [5. KavachAI DSL Grammar Specification](#5-kavachai-dsl-grammar-specification)
- [6. Database Schema — SQLite Audit Trail](#6-database-schema--sqlite-audit-trail)
- [7. Redis Data Structures](#7-redis-data-structures)
- [8. Semantic Grounding Layer Architecture](#8-semantic-grounding-layer-architecture)
- [9. LLM Gateway Routing Logic](#9-llm-gateway-routing-logic)
- [10. LLM Evaluation Engine Architecture](#10-llm-evaluation-engine-architecture)
- [11. React Dashboard Component Hierarchy](#11-react-dashboard-component-hierarchy)
- [12. Deployment Architecture](#12-deployment-architecture)
- [13. Security Architecture](#13-security-architecture)
- [14. Zero Trust Evaluation Pipeline — Detailed Flow](#14-zero-trust-evaluation-pipeline--detailed-flow)
- [15. Project Structure](#15-project-structure)
- [16. Key Design Decisions](#16-key-design-decisions)
- [17. Acceptance Criteria Traceability](#17-acceptance-criteria-traceability)
- [18. Correctness Properties](#18-correctness-properties)

---

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SOC Dashboard (React / Vercel)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ Threat   │ │ Kill     │ │ Compliance│ │ Forensic │ │ Model Eval /     │  │
│  │ Feed     │ │ Chain    │ │ Posture   │ │ Mode     │ │ Grounding Report │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ REST + WebSocket
┌────────────────────────────────▼────────────────────────────────────────────┐
│                     KavachAI Core (FastAPI / Railway)                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    MCP Proxy Gateway (Port 3001)                     │    │
│  │  MCP Client ──► Tool_Call_Intercept ──► Eval Pipeline ──► MCP Server│    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────── Zero Trust Evaluation Pipeline ──────────────────┐    │
│  │ 1. Auth ► 2. Cap Token ► 3. DSL Policy ► 4. Threat ► 5. DPDP      │    │
│  │ ► 6. Ethics ► 7. PII Mask ► 8. LLM Reasoning ► 9. Semantic        │    │
│  │   Grounding ► 10. Attestation                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────────┐    │
│  │ Policy Engine│ │ Threat       │ │ DPDP Engine  │ │ Ethics Engine  │    │
│  │ (DSL/DFA)   │ │ Detector     │ │              │ │                │    │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────────┘    │
│                                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────────┐    │
│  │ LLM Gateway  │ │ LLM Eval    │ │ Semantic     │ │ Multi-Agent    │    │
│  │              │ │ Engine      │ │ Grounding    │ │ Governor       │    │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────────┘    │
│                                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────────┐    │
│  │ Identity Mgr │ │ Escalation  │ │ Audit Trail  │ │ MCP Safety Srv │    │
│  │              │ │ Manager     │ │ (Hash Chain) │ │                │    │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────────┘    │
└──────────┬──────────────────────────────┬───────────────────────────────────┘
           │                              │
    ┌──────▼──────┐                ┌──────▼──────┐
    │   Redis     │                │   SQLite    │
    │ (Real-time) │                │ (Audit/     │
    │             │                │  Persistent)│
    └─────────────┘                └─────────────┘
```

[↑ Back to Top](#table-of-contents)

## 2. Data Models

### 2.1 Agent Identity

```python
@dataclass
class AgentIdentity:
    agent_id: str                    # UUID
    public_key: str                  # Ed25519 public key (base64)
    private_key_hash: str            # SHA-256 hash of private key (never stored raw)
    capability_scope: list[str]      # Allowed tool names
    trust_score: float               # 0.0 - 1.0
    trust_level: TrustLevel          # TRUSTED | STANDARD | RESTRICTED | QUARANTINED
    tenant_id: str                   # Tenant isolation
    created_at: datetime
    revoked: bool

class TrustLevel(str, Enum):
    TRUSTED = "trusted"              # 0.8 - 1.0
    STANDARD = "standard"            # 0.5 - 0.79
    RESTRICTED = "restricted"        # 0.2 - 0.49
    QUARANTINED = "quarantined"      # 0.0 - 0.19
```

### 2.2 Capability Token

```python
@dataclass
class CapabilityToken:
    token_id: str                    # UUID
    agent_id: str                    # FK to AgentIdentity
    allowed_tools: list[ToolScope]   # Scoped tool permissions
    expires_at: datetime
    signature: str                   # Ed25519 signature over token payload
    tenant_id: str

@dataclass
class ToolScope:
    tool_name: str
    allowed_params: dict[str, Any]   # Parameter constraints (regex, ranges)
    resource_paths: list[str]        # Allowed resource path patterns
    max_calls_per_minute: int
```

### 2.3 Action Request / Verdict

```python
@dataclass
class ActionRequest:
    request_id: str                  # UUID
    agent_id: str
    session_id: str
    tool_name: str
    parameters: dict[str, Any]
    signature: str                   # Agent's Ed25519 signature
    timestamp: datetime
    reasoning_trace: str | None      # LLM chain-of-thought if available
    tenant_id: str

@dataclass
class ActionVerdict:
    verdict: VerdictType             # ALLOW | BLOCK | FLAG | ESCALATE | QUARANTINE
    reason: str
    matched_policies: list[str]      # Policy rule IDs that matched
    threat_score: float
    ethics_score: float
    grounding_score: float | None    # From Semantic Grounding Layer
    attestation: ActionAttestation | None
    reasoning_trace: DecisionExplanation

class VerdictType(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    FLAG = "flag"
    ESCALATE = "escalate"
    QUARANTINE = "quarantine"
```

### 2.4 Action Attestation

```python
@dataclass
class ActionAttestation:
    attestation_id: str
    request_id: str
    action_hash: str                 # SHA-256(tool_name + params + timestamp)
    agent_identity_hash: str
    verdict: VerdictType
    policy_results: list[PolicyResult]
    threat_score: float
    grounding_score: float | None
    timestamp: datetime
    kavachai_signature: str       # KavachAI's Ed25519 signature
```

### 2.5 Audit Entry (Hash Chain)

```python
@dataclass
class AuditEntry:
    entry_id: int                    # Monotonically increasing per session
    timestamp: datetime
    session_id: str
    tenant_id: str
    agent_identity_hash: str
    action_type: str
    action_parameters_hash: str
    action_verdict: VerdictType
    matched_policies: list[str]
    threat_score: float
    ethics_score: float
    grounding_score: float | None
    llm_reasoning: str | None        # Captured chain-of-thought
    model_provenance: ModelProvenanceRecord | None
    llm_cost: float | None
    trust_score_before: float
    trust_score_after: float
    previous_entry_hash: str         # Hash chain link
    entry_hash: str                  # SHA-256(entry_id || timestamp || ... || previous_entry_hash)
```

### 2.6 Kill Chain

```python
@dataclass
class KillChain:
    kill_chain_id: str
    session_id: str
    stages: list[KillChainStage]
    overall_threat_score: float
    detected_at: datetime
    is_stac_attack: bool             # Sequential Tool Attack Chain

@dataclass
class KillChainStage:
    stage_number: int
    category: str                    # reconnaissance | weaponization | delivery | exploitation | exfiltration | c2
    action_request_id: str
    description: str
    threat_score: float
    timestamp: datetime
```

### 2.7 Semantic Grounding Models

```python
@dataclass
class GroundingResult:
    output_id: str
    session_id: str
    grounding_score: float           # 0.0 - 1.0
    claims: list[ClaimVerification]
    schema_valid: bool
    deterministic_checks: list[ValidationCheck]
    verdict: str                     # GROUNDED | INSUFFICIENTLY_GROUNDED | BLOCKED

@dataclass
class ClaimVerification:
    claim_text: str
    source_attribution: SourceAttribution | None
    grounded: bool
    confidence: float

@dataclass
class SourceAttribution:
    source_type: str                 # knowledge_graph | document | tool_response | ontology
    source_id: str                   # Node ID, document ID, or tool attestation ID
    source_label: str                # Human-readable source description
    evidence_text: str               # The specific evidence supporting the claim

@dataclass
class ValidationCheck:
    check_type: str                  # numerical_consistency | date_validity | entity_existence | regulatory | cross_reference
    passed: bool
    details: str
```

### 2.8 LLM Evaluation Models

```python
@dataclass
class ModelSafetyScore:
    model_name: str
    model_version: str
    overall_score: int               # 0-100
    sub_scores: dict[str, int]       # prompt_injection_resistance, toxicity, bias, hallucination, accuracy, domain_specific
    evaluated_at: datetime
    benchmark_id: str
    passed: bool                     # overall_score >= threshold

@dataclass
class SafetyBenchmark:
    benchmark_id: str
    name: str
    test_suites: list[TestSuite]
    threshold: int                   # Default 70
    tenant_id: str

@dataclass
class TestSuite:
    suite_type: str                  # prompt_injection | toxicity | bias | hallucination | accuracy | domain_specific
    test_cases: list[TestCase]
    weight: float                    # Weight in overall score

@dataclass
class RedTeamResult:
    run_id: str
    model_name: str
    adversarial_cases_run: int
    vulnerabilities_found: int
    safety_score_delta: float        # Change since last evaluation
    degraded: bool
    run_at: datetime
```

[↑ Back to Top](#table-of-contents)

## 3. API Design

### 3.1 Core Evaluation API

```
POST /api/v1/evaluate
  Body: ActionRequest
  Response: ActionVerdict
  Auth: X-API-Key header
  Latency target: <100ms

POST /api/v1/agents/register
  Body: { name, capability_scope, tenant_id }
  Response: { agent_id, public_key, private_key, capability_token }

PUT /api/v1/agents/{agent_id}/capabilities
  Body: { allowed_tools: [ToolScope], expires_in_seconds }
  Response: CapabilityToken

DELETE /api/v1/agents/{agent_id}
  Response: { revoked: true }
```

### 3.2 Session & Threat APIs

```
GET /api/v1/sessions/{session_id}/threat-profile
  Response: { threat_score, kill_chains, trust_score, trust_level, compliance_status, grounding_summary }

GET /api/v1/sessions/{session_id}/audit-trail
  Query: ?start=<timestamp>&end=<timestamp>
  Response: { entries: [AuditEntry], hash_chain_valid: bool }

GET /api/v1/sessions/{session_id}/grounding-report
  Response: { grounding_score, claims: [ClaimVerification], deterministic_checks }

POST /api/v1/sessions/{session_id}/replay
  Response: { trajectory_determinism, decision_determinism, divergences }
```

### 3.3 Policy Management APIs

```
PUT /api/v1/policies
  Body: { dsl_source: string, name: string }
  Response: { policy_id, verification_certificate, warnings }
  Note: Triggers formal verification before activation. Hot reload within 5s.

GET /api/v1/policies
  Response: [{ policy_id, name, status, verification_status, rule_count }]

GET /api/v1/policies/{policy_id}
  Response: { dsl_source, ast_summary, verification_certificate }

POST /api/v1/policies/{policy_id}/verify
  Response: { consistent, complete, conflicts, verification_certificate }
```

### 3.4 Escalation APIs

```
GET /api/v1/escalations
  Query: ?status=pending&sort=threat_score
  Response: [{ escalation_id, action_request, threat_score, kill_chain_context, timeout_at }]

POST /api/v1/escalations/{escalation_id}/resolve
  Body: { decision: "approve" | "reject", reason: string, operator_id: string }
  Response: { resolved: true, action_verdict }
```

### 3.5 LLM Gateway APIs

```
POST /api/v1/llm/completions
  Body: { model: string | null, messages, agent_id, session_id }
  Response: { completion, model_used, tokens, cost, safety_scan_result }
  Note: If model is null, uses intelligent routing.

GET /api/v1/llm/models
  Response: [{ model_name, provider, status, safety_score, cost_per_1k_tokens }]

GET /api/v1/llm/usage
  Query: ?agent_id=&session_id=&period=
  Response: { total_tokens, total_cost, breakdown_by_model, budget_remaining }
```

### 3.6 LLM Evaluation APIs

```
POST /api/v1/llm/evaluate/{model_name}
  Body: { benchmark_id: string | null }
  Response: { evaluation_id, model_safety_score, sub_scores, passed }

POST /api/v1/llm/red-team/{model_name}
  Response: { run_id, status: "started" }

GET /api/v1/llm/evaluations/{model_name}/history
  Response: [ModelSafetyScore]

GET /api/v1/llm/compare
  Query: ?models=model1,model2
  Response: { comparison: [{ model, safety_score, sub_scores, cost }] }
```

### 3.7 Compliance & Reporting APIs

```
GET /api/v1/compliance/dpdp-status
  Response: { overall_status, consent_coverage, localization_compliance, pii_masking_rate }

GET /api/v1/compliance/seven-sutras
  Response: { scores: { trust, people_first, innovation, fairness, accountability, understandable, safety } }

POST /api/v1/incidents/{incident_id}/export
  Response: EvidencePackage (binary, signed)

GET /api/v1/incidents/{incident_id}/report
  Response: IncidentReport (CERT-In format)
```

### 3.8 WebSocket — Real-Time Dashboard Feed

```
WS /ws/dashboard
  Auth: X-API-Key as query param
  Server pushes:
    { type: "threat_update", session_id, threat_score, action_summary }
    { type: "escalation", escalation_id, action_request, threat_score }
    { type: "kill_chain", session_id, kill_chain }
    { type: "quarantine", session_id, agent_id, reason }
    { type: "trust_change", agent_id, old_score, new_score, old_level, new_level }
    { type: "grounding_alert", session_id, grounding_score, ungrounded_claims }
    { type: "model_drift", model_name, metric, baseline, current }
    { type: "safety_degradation", model_name, old_score, new_score }
    { type: "budget_warning", agent_id, budget_used_pct }
```

[↑ Back to Top](#table-of-contents)

## 4. MCP Proxy Architecture

```
┌──────────────┐     MCP (stdio/SSE)     ┌──────────────────────────────┐     MCP (stdio/SSE)     ┌──────────────┐
│  MCP Client  │ ◄──────────────────────► │   MCP Proxy Gateway (:3001)  │ ◄──────────────────────► │  MCP Server  │
│  (AI Agent)  │                          │                              │                          │  (Tools)     │
│              │                          │  ┌────────────────────────┐  │                          │              │
│  Claude      │   tools/list ──────────► │  │ Tool_Discovery_Filter  │  │ ──► tools/list ────────► │  File System │
│  LangChain   │   ◄── filtered list ──── │  │ (hide unauthorized)    │  │ ◄── full list ────────── │  Database    │
│  CrewAI      │                          │  └────────────────────────┘  │                          │  APIs        │
│  AutoGen     │   tools/call ──────────► │  ┌────────────────────────┐  │                          │              │
│  Custom      │                          │  │ Tool_Call_Intercept    │  │                          │              │
│              │                          │  │  ├─ Build ActionRequest│  │                          │              │
│              │                          │  │  ├─ Run Eval Pipeline  │  │                          │              │
│              │                          │  │  ├─ ALLOW → forward   │──┼──► tools/call ──────────► │              │
│              │   ◄── tool result ────── │  │  ├─ BLOCK → error     │  │ ◄── result ──────────── │              │
│              │   ◄── JSON-RPC error ─── │  │  └─ ESCALATE → hold   │  │                          │              │
│              │                          │  └────────────────────────┘  │                          │              │
└──────────────┘                          │                              │                          └──────────────┘
                                          │  ┌────────────────────────┐  │
                                          │  │ Capability_Label       │  │
                                          │  │ Attachment             │  │
                                          │  │ (category, trust_level)│  │
                                          │  └────────────────────────┘  │
                                          └──────────────────────────────┘
```

### MCP Proxy Implementation

```python
class MCPProxyGateway:
    """Transparent proxy between MCP clients and MCP servers."""

    def __init__(self, eval_pipeline: EvalPipeline, config: ProxyConfig):
        self.eval_pipeline = eval_pipeline
        self.downstream_servers: dict[str, MCPServerConnection] = {}
        self.tool_routing: dict[str, str] = {}  # tool_name -> server_id

    async def handle_tools_list(self, client_id: str, agent_id: str) -> list[ToolDef]:
        """Aggregate tools from all downstream servers, filter by capability token."""
        all_tools = []
        for server_id, conn in self.downstream_servers.items():
            tools = await conn.list_tools()
            all_tools.extend(tools)

        # Filter by agent's capability token
        token = await self.get_capability_token(agent_id)
        filtered = [t for t in all_tools if t.name in token.allowed_tools_names]

        # Attach capability labels
        for tool in filtered:
            tool.metadata["capability_label"] = self.get_capability_label(tool.name)

        return filtered

    async def handle_tools_call(self, client_id: str, agent_id: str,
                                 tool_name: str, arguments: dict) -> ToolResult:
        """Intercept tool call, run eval pipeline, forward or block."""
        action_request = ActionRequest(
            request_id=uuid4(),
            agent_id=agent_id,
            session_id=self.get_session(client_id),
            tool_name=tool_name,
            parameters=arguments,
            timestamp=datetime.utcnow(),
        )

        verdict = await self.eval_pipeline.evaluate(action_request)

        if verdict.verdict == VerdictType.ALLOW:
            server_id = self.tool_routing[tool_name]
            result = await self.downstream_servers[server_id].call_tool(tool_name, arguments)
            return result
        elif verdict.verdict == VerdictType.BLOCK:
            raise MCPError(code=-32600, message=f"Blocked: {verdict.reason}")
        elif verdict.verdict == VerdictType.ESCALATE:
            decision = await self.escalation_manager.wait_for_decision(verdict)
            if decision.approved:
                return await self.downstream_servers[self.tool_routing[tool_name]].call_tool(tool_name, arguments)
            raise MCPError(code=-32600, message=f"Rejected by operator: {decision.reason}")
```

### MCP Safety Server

```python
class MCPSafetyServer:
    """MCP server exposing safety tools to agents."""

    tools = [
        Tool("check_policy", "Check if a proposed action would be allowed"),
        Tool("get_my_permissions", "Get current capability scope and trust level"),
        Tool("request_escalation", "Request human review of a planned action"),
        Tool("get_compliance_status", "Get DPDP compliance posture"),
        Tool("report_suspicious_input", "Report potentially malicious input"),
    ]

    async def check_policy(self, agent_id: str, proposed_action: dict) -> dict:
        """Dry-run policy evaluation without recording in audit trail."""
        action_request = ActionRequest.from_proposed(agent_id, proposed_action)
        verdict = await self.eval_pipeline.evaluate(action_request, dry_run=True)
        return {"verdict": verdict.verdict, "matched_rules": verdict.matched_policies,
                "reasoning": verdict.reasoning_trace}
```

[↑ Back to Top](#table-of-contents)

## 5. KavachAI DSL Grammar Specification

### PEG Grammar (Simplified)

```peg
# KavachAI DSL — PEG Grammar
# Trigger-Predicate-Enforcement pattern with LTL operators

Policy          <- Header Import* RuleBlock+ EOF
Header          <- 'policy' Identifier Version? Description?
Version         <- 'version' String
Description     <- 'description' String
Import          <- 'import' Identifier ('from' String)?

RuleBlock       <- 'rule' Identifier '{' Trigger Predicate Enforcement '}'
Trigger         <- 'when' TriggerExpr
TriggerExpr     <- ToolCallTrigger / StateTrigger / TemporalTrigger
ToolCallTrigger <- 'tool_call' '(' ToolPattern ')'
StateTrigger    <- 'state' '(' StateExpr ')'
TemporalTrigger <- LTLOperator '(' TriggerExpr ')'

Predicate       <- 'check' PredicateExpr
PredicateExpr   <- Comparison / LogicalExpr / TemporalPred / FlowPred
Comparison      <- FieldRef CompOp Value
LogicalExpr     <- PredicateExpr ('and' / 'or') PredicateExpr
TemporalPred    <- 'within' Duration 'of' ActionRef
FlowPred        <- 'data_from' Source 'reaches' Destination

Enforcement     <- 'then' Action Severity?
Action          <- 'allow' / 'block' / 'flag' / 'escalate' / 'quarantine'
Severity        <- 'severity' ('low' / 'medium' / 'high' / 'critical')

# LTL Operators
LTLOperator     <- 'always' / 'eventually' / 'until' / 'next'

# DFA Workflow Definition
Workflow        <- 'workflow' Identifier '{' State+ Transition+ '}'
State           <- 'state' Identifier StateType?
StateType       <- 'initial' / 'accepting' / 'dangerous'
Transition      <- Identifier '->' Identifier 'on' ToolPattern Guard?
Guard           <- 'if' PredicateExpr

# Parameterized Templates
Template        <- 'template' Identifier '(' ParamList ')' '{' RuleBlock+ '}'
ParamList       <- Param (',' Param)*
Param           <- Identifier ':' Type ('=' Default)?

# Ethics Constructs
EthicsRule      <- 'ensure' EthicsDimension 'in' Scope 'for' Target
EthicsDimension <- 'fairness' / 'safety' / 'transparency' / 'accountability'

# Primitives
Identifier      <- [a-zA-Z_][a-zA-Z0-9_]*
String          <- '"' [^"]* '"'
Duration        <- Number ('ms' / 's' / 'm' / 'h')
Number          <- [0-9]+
FieldRef        <- Identifier ('.' Identifier)*
Value           <- String / Number / Boolean / List
```

### DSL Example — Financial Services Policy

```
policy financial_services_safety
version "1.0"
description "Safety policies for financial services AI agents"

import dpdp_india from "modules/dpdp.shield"
import pii_rules from "modules/pii.shield"

rule block_unauthorized_payment {
  when tool_call("payment_process")
  check action.params.amount > 50000
    and agent.trust_level != "trusted"
  then escalate severity critical
}

rule temporal_data_access_restriction {
  when tool_call("customer_lookup")
  check within 5m of tool_call("external_api")
  then block severity high
}

rule prevent_aadhaar_exfiltration {
  when tool_call("send_email" | "external_api" | "webhook")
  check data_from "customer_records" reaches "external"
  then quarantine severity critical
}

rule always_mask_pii {
  when always(tool_call("*"))
  check output contains_pii("aadhaar" | "pan" | "mobile")
  then flag severity medium
}

workflow customer_service {
  state start initial
  state authenticated
  state data_accessed
  state response_sent accepting
  state admin_access dangerous

  start -> authenticated on tool_call("verify_identity")
  authenticated -> data_accessed on tool_call("customer_lookup")
  data_accessed -> response_sent on tool_call("send_response")
  authenticated -> admin_access on tool_call("admin_*")
}

ensure fairness in loan_processing for all demographic_groups
```

[↑ Back to Top](#table-of-contents)

## 6. Database Schema — SQLite Audit Trail

```sql
-- Core audit trail with hash chain integrity
CREATE TABLE audit_entries (
    entry_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT NOT NULL,          -- ISO 8601
    session_id      TEXT NOT NULL,
    tenant_id       TEXT NOT NULL,
    agent_identity_hash TEXT NOT NULL,
    action_type     TEXT NOT NULL,          -- tool name
    action_params_hash TEXT NOT NULL,       -- SHA-256 of params JSON
    action_verdict  TEXT NOT NULL,          -- allow|block|flag|escalate|quarantine
    matched_policies TEXT,                  -- JSON array of policy IDs
    threat_score    REAL NOT NULL DEFAULT 0.0,
    ethics_score    REAL DEFAULT NULL,
    grounding_score REAL DEFAULT NULL,
    llm_reasoning   TEXT,                   -- Chain-of-thought capture
    model_name      TEXT,                   -- LLM model used
    model_version   TEXT,
    llm_tokens      INTEGER,
    llm_cost        REAL,
    trust_score_before REAL,
    trust_score_after  REAL,
    previous_entry_hash TEXT NOT NULL,      -- Hash chain link (empty for first entry)
    entry_hash      TEXT NOT NULL UNIQUE,   -- SHA-256 of all fields + previous_hash
    sequence_number INTEGER NOT NULL        -- Monotonic per session, detects deletions
);

CREATE INDEX idx_audit_session ON audit_entries(session_id, sequence_number);
CREATE INDEX idx_audit_tenant ON audit_entries(tenant_id, timestamp);
CREATE INDEX idx_audit_agent ON audit_entries(agent_identity_hash, timestamp);

-- Agent registrations
CREATE TABLE agents (
    agent_id        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    public_key      TEXT NOT NULL,          -- Ed25519 base64
    capability_scope TEXT NOT NULL,         -- JSON array
    trust_score     REAL NOT NULL DEFAULT 0.5,
    trust_level     TEXT NOT NULL DEFAULT 'standard',
    tenant_id       TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    revoked         INTEGER NOT NULL DEFAULT 0,
    last_active_at  TEXT
);

-- Capability tokens
CREATE TABLE capability_tokens (
    token_id        TEXT PRIMARY KEY,
    agent_id        TEXT NOT NULL REFERENCES agents(agent_id),
    allowed_tools   TEXT NOT NULL,          -- JSON array of ToolScope
    expires_at      TEXT NOT NULL,
    signature       TEXT NOT NULL,
    tenant_id       TEXT NOT NULL,
    revoked         INTEGER NOT NULL DEFAULT 0
);

-- Policy storage
CREATE TABLE policies (
    policy_id       TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    dsl_source      TEXT NOT NULL,
    ast_json        TEXT NOT NULL,          -- Compiled AST
    verification_cert TEXT,                 -- JSON verification certificate
    status          TEXT NOT NULL DEFAULT 'active', -- active|inactive|failed_verification
    tenant_id       TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- DFA behavioral models
CREATE TABLE dfa_models (
    model_id        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    states          TEXT NOT NULL,          -- JSON: [{id, type, label}]
    transitions     TEXT NOT NULL,          -- JSON: [{from, to, tool_pattern, guard}]
    tenant_id       TEXT NOT NULL
);

-- Kill chains
CREATE TABLE kill_chains (
    kill_chain_id   TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL,
    stages          TEXT NOT NULL,          -- JSON array of KillChainStage
    overall_threat  REAL NOT NULL,
    is_stac_attack  INTEGER NOT NULL DEFAULT 0,
    detected_at     TEXT NOT NULL,
    tenant_id       TEXT NOT NULL
);

-- Escalations
CREATE TABLE escalations (
    escalation_id   TEXT PRIMARY KEY,
    action_request  TEXT NOT NULL,          -- JSON ActionRequest
    threat_score    REAL NOT NULL,
    kill_chain_id   TEXT,
    status          TEXT NOT NULL DEFAULT 'pending', -- pending|approved|rejected|timeout
    operator_id     TEXT,
    operator_reason TEXT,
    timeout_at      TEXT NOT NULL,
    resolved_at     TEXT,
    tenant_id       TEXT NOT NULL
);

-- LLM model evaluations
CREATE TABLE model_evaluations (
    evaluation_id   TEXT PRIMARY KEY,
    model_name      TEXT NOT NULL,
    model_version   TEXT NOT NULL,
    overall_score   INTEGER NOT NULL,       -- 0-100
    sub_scores      TEXT NOT NULL,          -- JSON dict
    benchmark_id    TEXT NOT NULL,
    passed          INTEGER NOT NULL,
    evaluated_at    TEXT NOT NULL,
    tenant_id       TEXT NOT NULL
);

-- Red team runs
CREATE TABLE red_team_runs (
    run_id          TEXT PRIMARY KEY,
    model_name      TEXT NOT NULL,
    cases_run       INTEGER NOT NULL,
    vulnerabilities INTEGER NOT NULL,
    safety_delta    REAL NOT NULL,
    degraded        INTEGER NOT NULL DEFAULT 0,
    run_at          TEXT NOT NULL,
    tenant_id       TEXT NOT NULL
);

-- Knowledge graphs for semantic grounding
CREATE TABLE knowledge_graphs (
    graph_id        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    domain          TEXT NOT NULL,
    nodes           TEXT NOT NULL,          -- JSON: [{id, type, label, properties}]
    edges           TEXT NOT NULL,          -- JSON: [{from, to, relation, properties}]
    source_type     TEXT NOT NULL,          -- local_json | neo4j | api
    source_config   TEXT,                   -- Connection config JSON
    tenant_id       TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- Domain ontologies
CREATE TABLE domain_ontologies (
    ontology_id     TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    domain          TEXT NOT NULL,
    concepts        TEXT NOT NULL,          -- JSON: [{name, properties, constraints}]
    relationships   TEXT NOT NULL,          -- JSON: [{from, to, type, constraints}]
    tenant_id       TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- Grounding results
CREATE TABLE grounding_results (
    result_id       TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL,
    output_id       TEXT NOT NULL,
    grounding_score REAL NOT NULL,
    claims          TEXT NOT NULL,          -- JSON array of ClaimVerification
    schema_valid    INTEGER NOT NULL,
    deterministic_checks TEXT NOT NULL,     -- JSON array of ValidationCheck
    verdict         TEXT NOT NULL,
    tenant_id       TEXT NOT NULL,
    created_at      TEXT NOT NULL
);

-- Tenants
CREATE TABLE tenants (
    tenant_id       TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    api_key_hash    TEXT NOT NULL,          -- Salted SHA-256
    llm_budget      REAL,
    rate_limit      INTEGER,               -- Max actions per minute
    config          TEXT NOT NULL,          -- JSON tenant config
    created_at      TEXT NOT NULL
);
```

[↑ Back to Top](#table-of-contents)

## 7. Redis Data Structures

```
# Session state — real-time threat tracking
session:{session_id}:threat_score     → FLOAT (current session threat score)
session:{session_id}:action_window    → LIST (last 50 action hashes for pattern correlation)
session:{session_id}:dfa_state        → STRING (current DFA state ID)
session:{session_id}:cumulative_effects → HASH {
    data_accessed: JSON list of data sources,
    tools_called: JSON list of tool names,
    permissions_used: JSON list of capabilities,
    data_flows: JSON list of {source, destination} pairs
}
session:{session_id}:grounding_context → HASH {
    tool_responses: JSON map of tool_call_id → response,
    claims_verified: INT count,
    claims_ungrounded: INT count
}

# Agent trust scores — fast lookup
agent:{agent_id}:trust_score          → FLOAT
agent:{agent_id}:trust_level          → STRING (trusted|standard|restricted|quarantined)
agent:{agent_id}:last_active          → TIMESTAMP

# Capability tokens — fast validation
token:{token_id}                      → HASH { agent_id, allowed_tools (JSON), expires_at }
token:{token_id}:revoked              → BOOL

# Rate limiting
rate:{agent_id}:{tool_name}:{window}  → INT (call count, with TTL = window duration)
rate:{tenant_id}:global:{window}      → INT (tenant-level rate limit)

# Escalation queue
escalation:queue                      → SORTED SET (score = threat_score, member = escalation_id)
escalation:{escalation_id}            → HASH { action_request, threat_score, timeout_at, status }

# LLM budget tracking
budget:{agent_id}:tokens              → INT (cumulative tokens used)
budget:{agent_id}:cost                → FLOAT (cumulative cost USD)
budget:{session_id}:tokens            → INT
budget:{session_id}:cost              → FLOAT
budget:{tenant_id}:cost:{period}      → FLOAT (e.g., budget:t1:cost:2025-07)

# Model health — real-time observability
model:{model_name}:latency            → SORTED SET (score = timestamp, member = latency_ms)
model:{model_name}:errors             → INT (with TTL window)
model:{model_name}:refusals           → INT (with TTL window)
model:{model_name}:baseline           → HASH { latency_p95, error_rate, refusal_rate }
model:{model_name}:safety_score       → INT (latest Model_Safety_Score)

# Real-time dashboard pub/sub
channel:dashboard:{tenant_id}         → PUB/SUB channel for WebSocket feed
```

[↑ Back to Top](#table-of-contents)

## 8. Semantic Grounding Layer Architecture

```
                    Agent LLM Response
                          │
                          ▼
              ┌───────────────────────┐
              │  Schema Enforcer      │  ◄── JSON Schema definitions
              │  (structural check)   │
              └───────────┬───────────┘
                          │ (schema valid)
                          ▼
              ┌───────────────────────┐
              │  Claim Extractor      │  Extracts factual claims from output
              │  (NLP / regex-based)  │
              └───────────┬───────────┘
                          │ [claim1, claim2, ...]
                          ▼
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ Knowledge   │  │ Tool Response│  │ Domain       │
│ Graph       │  │ Verifier     │  │ Ontology     │
│ Lookup      │  │              │  │ Validator    │
│             │  │ Compare claim│  │              │
│ Entity/fact │  │ vs actual    │  │ Concept/     │
│ verification│  │ tool receipts│  │ constraint   │
│             │  │ (attestations│  │ validation   │
└──────┬──────┘  └──────┬───────┘  └──────┬───────┘
       │                │                  │
       └────────────────┼──────────────────┘
                        ▼
              ┌───────────────────────┐
              │  Deterministic        │
              │  Validator            │
              │  ├─ Numerical checks  │
              │  ├─ Date/time checks  │
              │  ├─ Entity existence  │
              │  ├─ Regulatory checks │
              │  └─ Cross-reference   │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Grounding Scorer     │
              │                       │
              │  grounding_score =    │
              │    grounded_claims /  │
              │    total_claims       │
              │                       │
              │  Attach Source        │
              │  Attributions         │
              └───────────┬───────────┘
                          │
                    ┌─────┴─────┐
                    │           │
              score >= 0.7  score < 0.7
                    │           │
                    ▼           ▼
              GROUNDED    INSUFFICIENTLY_GROUNDED
              (pass)      ├─ strict mode → BLOCK
                          └─ advisory mode → WARN + attach warning
```

### Implementation

```python
class SemanticGroundingLayer:
    """Deterministic validation layer — no LLM dependency."""

    def __init__(self, knowledge_graphs: list[KnowledgeGraph],
                 ontologies: list[DomainOntology],
                 schemas: dict[str, JSONSchema]):
        self.kg_store = KnowledgeGraphStore(knowledge_graphs)
        self.ontology_store = OntologyStore(ontologies)
        self.schema_enforcer = SchemaEnforcer(schemas)
        self.claim_extractor = ClaimExtractor()
        self.deterministic_validator = DeterministicValidator()

    async def validate(self, agent_output: str, session_context: SessionContext,
                       output_schema: str | None = None) -> GroundingResult:
        # Step 1: Schema enforcement
        if output_schema:
            schema_result = self.schema_enforcer.validate(agent_output, output_schema)
            if not schema_result.valid:
                return GroundingResult(grounding_score=0.0, schema_valid=False,
                                       verdict="BLOCKED", claims=[], deterministic_checks=[])

        # Step 2: Extract claims
        claims = self.claim_extractor.extract(agent_output)

        # Step 3: Verify each claim against knowledge sources
        verified_claims = []
        for claim in claims:
            attribution = None
            # Check knowledge graph
            kg_match = self.kg_store.verify_claim(claim)
            if kg_match:
                attribution = SourceAttribution(source_type="knowledge_graph", **kg_match)
            # Check tool responses from session
            elif tool_match := session_context.match_tool_response(claim):
                attribution = SourceAttribution(source_type="tool_response", **tool_match)
            # Check ontology constraints
            elif onto_match := self.ontology_store.verify_claim(claim):
                attribution = SourceAttribution(source_type="ontology", **onto_match)

            verified_claims.append(ClaimVerification(
                claim_text=claim.text, source_attribution=attribution,
                grounded=attribution is not None, confidence=attribution.confidence if attribution else 0.0
            ))

        # Step 4: Deterministic validation
        det_checks = self.deterministic_validator.run_all(agent_output, session_context)

        # Step 5: Compute grounding score
        grounded_count = sum(1 for c in verified_claims if c.grounded)
        total = max(len(verified_claims), 1)
        grounding_score = grounded_count / total

        verdict = "GROUNDED" if grounding_score >= session_context.grounding_threshold else "INSUFFICIENTLY_GROUNDED"

        return GroundingResult(
            grounding_score=grounding_score, schema_valid=True,
            claims=verified_claims, deterministic_checks=det_checks, verdict=verdict
        )
```

[↑ Back to Top](#table-of-contents)

## 9. LLM Gateway Routing Logic

```
┌──────────────────────────────────────────────────────────────────┐
│                        LLM Gateway                                │
│                                                                   │
│  Agent Request ──► LLM_Request_Interceptor (pre-scan)            │
│                         │                                         │
│                         ▼                                         │
│                   ┌─────────────┐                                 │
│                   │ Router      │                                 │
│                   │             │                                 │
│                   │ 1. Check    │                                 │
│                   │    budget   │──► BUDGET_EXCEEDED → block      │
│                   │ 2. Select   │                                 │
│                   │    model    │                                 │
│                   │ 3. Check    │                                 │
│                   │    safety   │──► Model safety_score < 70 →    │
│                   │    score    │    skip to next in fallback     │
│                   └──────┬──────┘                                 │
│                          │                                        │
│              ┌───────────┼───────────┐                            │
│              ▼           ▼           ▼                            │
│         ┌────────┐ ┌────────┐ ┌──────────┐                       │
│         │OpenAI  │ │Anthropic│ │Google/   │                       │
│         │        │ │        │ │Ollama    │                       │
│         └───┬────┘ └───┬────┘ └────┬─────┘                       │
│             │          │           │                              │
│             └──────────┼───────────┘                              │
│                        ▼                                          │
│              LLM_Request_Interceptor (post-scan)                  │
│              ├─ Toxicity check                                    │
│              ├─ Bias check                                        │
│              ├─ Hallucination flag                                │
│              └─ Policy compliance                                 │
│                        │                                          │
│                        ▼                                          │
│              Track: tokens, cost, latency                         │
│              Record: Model_Provenance_Record                      │
│              Update: budget counters in Redis                     │
│                        │                                          │
│                        ▼                                          │
│              Return to Agent                                      │
└──────────────────────────────────────────────────────────────────┘
```

### Routing Strategy

```python
class LLMGateway:
    """Unified LLM gateway with safety governance and cost tracking."""

    async def route_request(self, request: LLMRequest) -> LLMResponse:
        # 1. Budget check
        budget = await self.redis.get_budget(request.agent_id, request.session_id, request.tenant_id)
        if budget.exceeded:
            raise BudgetExceededError(budget.details)

        # 2. Pre-scan prompt
        pre_scan = await self.request_interceptor.scan_prompt(request)
        if pre_scan.blocked:
            return LLMResponse(blocked=True, reason=pre_scan.reason)

        # 3. Select model (intelligent routing or explicit)
        model = request.model or await self.select_model(request)

        # 4. Verify model safety score
        safety_score = await self.redis.get(f"model:{model}:safety_score")
        if safety_score and int(safety_score) < self.min_safety_score:
            model = await self.get_fallback_model(model, request.tenant_id)

        # 5. Inject reasoning capture instruction
        messages = self.inject_reasoning_capture(request.messages)

        # 6. Call provider with fallback chain
        fallback_chain = await self.get_fallback_chain(model, request.tenant_id)
        response = None
        for candidate_model in [model] + fallback_chain:
            try:
                provider = self.providers[self.get_provider(candidate_model)]
                response = await provider.complete(candidate_model, messages)
                break
            except ProviderError:
                continue

        if not response:
            raise AllModelsFailedError()

        # 7. Post-scan response
        post_scan = await self.request_interceptor.scan_response(response)
        if post_scan.blocked:
            return LLMResponse(blocked=True, reason=post_scan.reason)

        # 8. Track usage
        await self.track_usage(request, response, candidate_model)

        return response

    async def select_model(self, request: LLMRequest) -> str:
        """Intelligent routing: simple queries → cheap model, complex → capable model."""
        complexity = self.estimate_complexity(request.messages)
        budget_remaining_pct = await self.get_budget_remaining_pct(request)

        if complexity == "low" or budget_remaining_pct < 0.5:
            return self.get_cheapest_model(request.tenant_id)
        elif complexity == "high":
            return self.get_most_capable_model(request.tenant_id)
        else:
            return self.get_default_model(request.tenant_id)
```

[↑ Back to Top](#table-of-contents)

## 10. LLM Evaluation Engine Architecture

```python
class LLMEvalEngine:
    """Systematic model evaluation before deployment and continuous monitoring."""

    async def evaluate_model(self, model_name: str, benchmark: SafetyBenchmark) -> ModelSafetyScore:
        sub_scores = {}
        for suite in benchmark.test_suites:
            score = await self.run_test_suite(model_name, suite)
            sub_scores[suite.suite_type] = score

        overall = sum(sub_scores[s.suite_type] * s.weight for s in benchmark.test_suites)
        passed = overall >= benchmark.threshold

        result = ModelSafetyScore(
            model_name=model_name, overall_score=int(overall),
            sub_scores=sub_scores, passed=passed, evaluated_at=datetime.utcnow(),
            benchmark_id=benchmark.benchmark_id
        )

        # Store in audit trail
        await self.audit_trail.record_evaluation(result)
        # Update Redis cache
        await self.redis.set(f"model:{model_name}:safety_score", int(overall))

        return result

    async def run_test_suite(self, model_name: str, suite: TestSuite) -> int:
        """Run a test suite and return score 0-100."""
        results = []
        for case in suite.test_cases:
            response = await self.llm_gateway.raw_complete(model_name, case.prompt)
            passed = case.evaluator(response)
            results.append(passed)
        return int(sum(results) / len(results) * 100)


class RedTeamRunner:
    """Automated adversarial testing on a schedule."""

    ATTACK_GENERATORS = {
        "prompt_injection": PromptInjectionGenerator,
        "jailbreak": JailbreakGenerator,
        "bias_trigger": BiasTriggerGenerator,
    }

    async def run(self, model_name: str) -> RedTeamResult:
        cases_run = 0
        vulnerabilities = 0

        for attack_type, generator in self.ATTACK_GENERATORS.items():
            test_cases = generator.generate(count=50)
            for case in test_cases:
                cases_run += 1
                response = await self.llm_gateway.raw_complete(model_name, case.prompt)
                if case.is_vulnerable(response):
                    vulnerabilities += 1

        # Compare with last evaluation
        last_score = await self.get_last_safety_score(model_name)
        current_vuln_rate = vulnerabilities / max(cases_run, 1)
        safety_delta = -current_vuln_rate * 100  # Negative = degradation

        return RedTeamResult(
            model_name=model_name, adversarial_cases_run=cases_run,
            vulnerabilities_found=vulnerabilities, safety_score_delta=safety_delta,
            degraded=abs(safety_delta) > 10, run_at=datetime.utcnow()
        )
```

[↑ Back to Top](#table-of-contents)

## 11. React Dashboard Component Hierarchy

```
SOCDashboard (App)
├── Layout
│   ├── Sidebar
│   │   ├── NavItem: Threat Feed
│   │   ├── NavItem: Kill Chains
│   │   ├── NavItem: Compliance
│   │   ├── NavItem: Forensics
│   │   ├── NavItem: Model Registry
│   │   ├── NavItem: Model Evaluation
│   │   ├── NavItem: Grounding Reports
│   │   ├── NavItem: LLM Usage & Cost
│   │   ├── NavItem: Policies
│   │   ├── NavItem: Agents
│   │   └── NavItem: Settings
│   └── TopBar
│       ├── TenantSelector
│       ├── AlertBadge (real-time count)
│       └── UserMenu
│
├── Pages
│   ├── ThreatFeedPage
│   │   ├── LiveSessionTable (sortable by threat_score)
│   │   ├── ThreatScoreGauge (per session)
│   │   ├── AlertPanel (QUARANTINE, escalations, hash violations)
│   │   └── RealTimeChart (actions/sec, threats/min)
│   │
│   ├── KillChainPage
│   │   ├── KillChainGraph (directed graph visualization)
│   │   ├── StageDetailPanel
│   │   ├── STACAttackIndicator
│   │   └── TimelineView
│   │
│   ├── CompliancePage
│   │   ├── DPDPStatusCard (consent, localization, PII masking)
│   │   ├── SevenSutrasRadarChart
│   │   ├── ComplianceTrendChart
│   │   └── ExportReportButton
│   │
│   ├── ForensicPage
│   │   ├── SessionSelector
│   │   ├── ActionTimeline (step-by-step replay)
│   │   ├── ActionDetailPanel
│   │   │   ├── AttestationView
│   │   │   ├── ReasoningTraceView (3-layer: LLM, Policy, User-facing)
│   │   │   ├── CapabilityTokenView
│   │   │   └── GroundingDetailView (claim → source)
│   │   ├── SessionComparisonView (side-by-side)
│   │   ├── DeterminismReplayPanel
│   │   └── EvidenceExportButton
│   │
│   ├── ModelRegistryPage
│   │   ├── ModelCardList
│   │   ├── ModelCardDetail (limitations, bias, suitability)
│   │   ├── ModelPerformanceChart
│   │   └── ModelTransparencyReport
│   │
│   ├── ModelEvaluationPage
│   │   ├── SafetyScoreOverview (all models, current scores)
│   │   ├── BenchmarkBreakdownChart (per model, per category)
│   │   ├── HistoricalScoreTrend (line chart over time)
│   │   ├── HeadToHeadComparison (side-by-side model comparison)
│   │   ├── RedTeamResultsPanel
│   │   └── EvaluationReportExport
│   │
│   ├── GroundingReportsPage
│   │   ├── SessionGroundingTable (session_id, grounding_score, claims)
│   │   ├── ClaimVerificationList (claim → source attribution)
│   │   ├── DeterministicCheckResults
│   │   ├── UngroundedClaimsHighlight
│   │   └── GroundingTrendChart
│   │
│   ├── LLMUsagePage
│   │   ├── CostDashboard (by model, agent, session, time)
│   │   ├── BudgetUtilizationGauge
│   │   ├── TokenUsageChart
│   │   ├── ModelHealthPanel (latency, errors, refusals — traffic lights)
│   │   ├── DriftAlertList
│   │   └── CostProjectionChart
│   │
│   ├── PolicyPage
│   │   ├── PolicyList
│   │   ├── DSLEditor (Monaco-based with syntax highlighting)
│   │   ├── VisualPolicyBuilder (drag-and-drop)
│   │   ├── VerificationResultPanel
│   │   ├── PolicyEffectivenessMetrics
│   │   └── DFAVisualEditor (state diagram)
│   │
│   ├── AgentsPage
│   │   ├── AgentTable (trust score, level, status)
│   │   ├── TrustScoreHistory (per agent)
│   │   ├── DelegationChainGraph
│   │   └── AgentRegistrationForm
│   │
│   └── EscalationPage
│       ├── EscalationQueue (sorted by threat_score)
│       ├── EscalationDetailPanel
│       │   ├── ActionRequestView
│       │   ├── ThreatAnalysisView
│       │   ├── KillChainContextView
│       │   └── ComplianceImpactView
│       └── ApproveRejectButtons
│
└── Shared Components
    ├── WebSocketProvider (real-time updates)
    ├── ThreatScoreBadge
    ├── TrustLevelBadge
    ├── GroundingScoreBadge
    ├── SafetyScoreBadge
    ├── VerdictChip (color-coded ALLOW/BLOCK/FLAG/ESCALATE/QUARANTINE)
    ├── HashChainIndicator
    ├── AudioAlertManager
    └── PDFExporter
```

[↑ Back to Top](#table-of-contents)

## 12. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Cloud Deployment                             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Vercel                                │    │
│  │  SOC Dashboard (React)                                   │    │
│  │  - Static build + API routes for SSR                     │    │
│  │  - Environment: NEXT_PUBLIC_API_URL=https://api.railway  │    │
│  │  - WebSocket proxy to Railway backend                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                       │
│                          │ HTTPS                                 │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Railway                               │    │
│  │                                                          │    │
│  │  ┌──────────────────────────────────────────────────┐   │    │
│  │  │  KavachAI Backend (FastAPI)                    │   │    │
│  │  │  - REST API (:8000)                              │   │    │
│  │  │  - MCP Proxy Gateway (:3001)                     │   │    │
│  │  │  - WebSocket endpoint (/ws/dashboard)            │   │    │
│  │  │  - MCP Safety Server                             │   │    │
│  │  │  - SQLite volume mount (/data/kavachai.db)    │   │    │
│  │  └──────────────────────────────────────────────────┘   │    │
│  │                                                          │    │
│  │  ┌──────────────────────────────────────────────────┐   │    │
│  │  │  Redis (Railway addon)                           │   │    │
│  │  │  - Real-time state, pub/sub, rate limiting       │   │    │
│  │  └──────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  Local Docker Fallback                            │
│                                                                  │
│  docker-compose.yml                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ kavachai  │  │ redis        │  │ dashboard            │  │
│  │ (FastAPI)    │  │ (:6379)      │  │ (React dev / nginx)  │  │
│  │ :8000, :3001 │  │              │  │ :3000                │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                  │
│  Volumes: ./data/kavachai.db (SQLite)                        │
│  Network: kavachai-net (internal)                            │
└─────────────────────────────────────────────────────────────────┘
```

### Docker Compose

```yaml
version: "3.8"
services:
  kavachai:
    build: ./backend
    ports:
      - "8000:8000"   # REST API
      - "3001:3001"   # MCP Proxy Gateway
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=sqlite:///data/kavachai.db
      - ENVIRONMENT=docker
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/data
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  dashboard:
    build: ./dashboard
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000
    depends_on:
      - kavachai
```

[↑ Back to Top](#table-of-contents)

## 13. Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Security Layers                               │
│                                                                  │
│  Layer 1: Transport Security                                     │
│  ├─ HTTPS/TLS for all REST and WebSocket connections            │
│  ├─ MCP transport encryption (SSE over HTTPS)                   │
│  └─ Redis TLS in cloud deployment                               │
│                                                                  │
│  Layer 2: Authentication                                         │
│  ├─ API Key authentication (X-API-Key header)                   │
│  │   └─ Keys stored as salted SHA-256 hashes                    │
│  ├─ Agent identity: Ed25519 key pairs                           │
│  │   └─ Every ActionRequest signed by agent's private key       │
│  └─ Tenant isolation: all queries scoped by tenant_id           │
│                                                                  │
│  Layer 3: Authorization                                          │
│  ├─ Capability Tokens: scoped, time-limited, signed             │
│  ├─ Tool-level access control via ToolScope                     │
│  ├─ Parameter-level constraints (regex, ranges)                 │
│  ├─ DFA state-based authorization (valid transitions only)      │
│  └─ Trust-level graduated enforcement                           │
│                                                                  │
│  Layer 4: Integrity                                              │
│  ├─ Hash chain audit trail (SHA-256 linked entries)             │
│  ├─ Monotonic sequence numbers (deletion detection)             │
│  ├─ Action attestations (KavachAI-signed receipts)           │
│  ├─ Evidence packages (cryptographically signed bundles)        │
│  └─ Startup hash chain verification                             │
│                                                                  │
│  Layer 5: Threat Detection                                       │
│  ├─ Prompt injection detection (direct + indirect)              │
│  ├─ Tool poisoning detection (schema/statistical deviation)     │
│  ├─ Privilege escalation detection (scope creep analysis)       │
│  ├─ Covert channel detection (steganography, encoding)          │
│  ├─ STAC attack detection (cumulative effect analysis)          │
│  ├─ Multi-agent collusion detection (cross-session graph)       │
│  └─ Kill chain correlation (sliding window, 50 actions)         │
│                                                                  │
│  Layer 6: Semantic Grounding (NEW)                               │
│  ├─ Schema enforcement (JSON schema validation)                 │
│  ├─ Knowledge graph verification (entity/fact checking)         │
│  ├─ Domain ontology validation (concept/constraint checking)    │
│  ├─ Deterministic validation (numerical, date, cross-ref)       │
│  ├─ Source attribution (claim → evidence traceability)          │
│  └─ No LLM dependency (fully deterministic)                     │
│                                                                  │
│  Layer 7: Compliance                                             │
│  ├─ DPDP Act 2023 enforcement (consent, localization, PII)     │
│  ├─ India AI Governance Guidelines (Seven Sutras mapping)       │
│  ├─ Ethics guardrails (bias, toxicity, fairness, content)       │
│  ├─ Right-to-explanation (multi-layer decision explanations)    │
│  └─ CERT-In incident reporting                                  │
│                                                                  │
│  Layer 8: LLM Safety Governance (NEW)                            │
│  ├─ Pre-deployment model evaluation (Safety_Benchmarks)         │
│  ├─ Continuous red-teaming (automated adversarial testing)      │
│  ├─ Model safety scoring (composite 0-100 score)               │
│  ├─ Safety degradation detection and alerting                   │
│  ├─ Model drift detection (behavioral baseline comparison)      │
│  └─ Budget enforcement (per-agent, per-session, per-org)        │
└─────────────────────────────────────────────────────────────────┘
```

[↑ Back to Top](#table-of-contents)

## 14. Zero Trust Evaluation Pipeline — Detailed Flow

```python
class EvalPipeline:
    """The 10-stage Zero Trust evaluation pipeline."""

    async def evaluate(self, request: ActionRequest, dry_run: bool = False) -> ActionVerdict:
        context = PipelineContext(request=request, dry_run=dry_run)

        stages = [
            ("auth", self.authenticate),
            ("cap_token", self.verify_capability_token),
            ("dsl_policy", self.evaluate_dsl_policies),
            ("threat", self.run_threat_detection),
            ("dpdp", self.check_dpdp_compliance),
            ("ethics", self.run_ethics_evaluation),
            ("pii_mask", self.apply_pii_masking),
            ("reasoning", self.capture_llm_reasoning),
            ("grounding", self.validate_semantic_grounding),
            ("attestation", self.generate_attestation),
        ]

        for stage_name, stage_fn in stages:
            result = await stage_fn(context)
            if result.verdict in (VerdictType.BLOCK, VerdictType.ESCALATE, VerdictType.QUARANTINE):
                # Short-circuit: halt pipeline, return verdict immediately
                if not dry_run:
                    await self.record_audit(context, result, halted_at=stage_name)
                    await self.update_trust_score(request.agent_id, result.verdict)
                    await self.publish_dashboard_event(context, result)
                return result

        # All stages passed
        final_verdict = ActionVerdict(
            verdict=VerdictType.ALLOW,
            threat_score=context.threat_score,
            ethics_score=context.ethics_score,
            grounding_score=context.grounding_score,
            attestation=context.attestation,
        )

        if not dry_run:
            await self.record_audit(context, final_verdict)
            await self.update_trust_score(request.agent_id, VerdictType.ALLOW)

        return final_verdict
```

[↑ Back to Top](#table-of-contents)

## 15. Project Structure

```
kavachai/
├── backend/
│   ├── main.py                      # FastAPI app entry point
│   ├── config.py                    # Environment-specific config
│   ├── models/                      # Pydantic data models
│   │   ├── agent.py                 # AgentIdentity, CapabilityToken, TrustLevel
│   │   ├── action.py                # ActionRequest, ActionVerdict, ActionAttestation
│   │   ├── audit.py                 # AuditEntry, EvidencePackage
│   │   ├── threat.py                # KillChain, ThreatScore
│   │   ├── grounding.py             # GroundingResult, ClaimVerification, SourceAttribution
│   │   ├── evaluation.py            # ModelSafetyScore, SafetyBenchmark, RedTeamResult
│   │   └── policy.py                # PolicyAST, VerificationCertificate
│   ├── core/
│   │   ├── pipeline.py              # EvalPipeline (10-stage)
│   │   ├── identity.py              # AgentIdentityManager
│   │   ├── policy_engine.py         # PolicyEngine, ProbabilisticRuleCircuit
│   │   ├── dsl_parser.py            # PEG parser for KavachAI DSL
│   │   ├── dsl_printer.py           # DSL pretty printer
│   │   ├── dfa_engine.py            # DFA behavioral model runtime
│   │   ├── trust_engine.py          # Dynamic trust scoring
│   │   └── formal_verifier.py       # Offline policy verification
│   ├── threat/
│   │   ├── detector.py              # ThreatDetector orchestrator
│   │   ├── prompt_injection.py      # PromptInjectionDetector
│   │   ├── tool_poisoning.py        # ToolPoisoningDetector
│   │   ├── privilege_escalation.py  # PrivilegeEscalationDetector
│   │   ├── covert_channel.py        # CovertChannelDetector
│   │   └── attack_chain.py          # AttackChainAnalyzer (STAC defense)
│   ├── compliance/
│   │   ├── dpdp_engine.py           # DPDP Act compliance
│   │   ├── pii_masker.py            # Aadhaar, PAN, mobile, UPI masking
│   │   ├── seven_sutras.py          # India AI Governance mapping
│   │   └── cert_in.py               # CERT-In incident reporting
│   ├── ethics/
│   │   ├── engine.py                # EthicsEngine orchestrator
│   │   ├── bias_detector.py         # India-specific bias detection
│   │   ├── toxicity_filter.py       # Content toxicity classification
│   │   ├── fairness_monitor.py      # Systematic fairness tracking
│   │   └── content_safety.py        # Content safety classifier
│   ├── grounding/
│   │   ├── layer.py                 # SemanticGroundingLayer
│   │   ├── schema_enforcer.py       # JSON schema validation
│   │   ├── claim_extractor.py       # Extract factual claims from output
│   │   ├── knowledge_graph.py       # KG store and query
│   │   ├── ontology.py              # Domain ontology validation
│   │   ├── deterministic_validator.py # Numerical, date, entity, regulatory checks
│   │   └── source_attribution.py    # Claim → source linking
│   ├── llm/
│   │   ├── gateway.py               # LLMGateway, routing, fallback
│   │   ├── providers/               # Provider adapters
│   │   │   ├── openai.py
│   │   │   ├── anthropic.py
│   │   │   ├── google.py
│   │   │   └── ollama.py
│   │   ├── interceptor.py           # LLMRequestInterceptor (pre/post scan)
│   │   ├── eval_engine.py           # LLMEvalEngine
│   │   ├── red_team.py              # RedTeamRunner
│   │   ├── observability.py         # LLMObservability, ModelDriftDetector
│   │   └── budget.py                # Budget tracking and enforcement
│   ├── mcp/
│   │   ├── proxy.py                 # MCPProxyGateway
│   │   ├── safety_server.py         # MCPSafetyServer
│   │   └── transport.py             # MCP transport (stdio, SSE)
│   ├── audit/
│   │   ├── trail.py                 # CryptographicAuditTrail
│   │   ├── hash_chain.py            # Hash chain operations
│   │   ├── evidence.py              # EvidencePackage generation
│   │   └── replay.py                # Determinism audit replay
│   ├── multi_agent/
│   │   ├── governor.py              # MultiAgentGovernor
│   │   ├── delegation.py            # DelegationChain tracking
│   │   └── collusion.py             # CollusionDetector
│   ├── explain/
│   │   ├── reasoning_capture.py     # LLMReasoningCapture
│   │   ├── decision_explanation.py  # Multi-layer explanations
│   │   └── templates.py             # ExplanationTemplates
│   ├── api/
│   │   ├── routes_eval.py           # /evaluate, /agents
│   │   ├── routes_session.py        # /sessions
│   │   ├── routes_policy.py         # /policies
│   │   ├── routes_escalation.py     # /escalations
│   │   ├── routes_llm.py            # /llm
│   │   ├── routes_compliance.py     # /compliance, /incidents
│   │   ├── routes_grounding.py      # /grounding
│   │   └── websocket.py             # WebSocket dashboard feed
│   ├── db/
│   │   ├── database.py              # SQLite connection, migrations
│   │   └── redis_client.py          # Redis connection, helpers
│   ├── demo/
│   │   ├── scenario.py              # Demo financial services attack
│   │   ├── demo_agent.py            # Demo agent with tools
│   │   ├── demo_policies.shield     # Demo DSL policies
│   │   ├── demo_dfa.shield          # Demo DFA workflow
│   │   ├── demo_knowledge_graph.json # Demo KG for financial services
│   │   └── demo_ontology.json       # Demo domain ontology
│   └── requirements.txt
│
├── dashboard/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/                   # Page components (see Section 11)
│   │   ├── components/              # Shared components
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts      # Real-time WebSocket hook
│   │   │   └── useApi.ts            # API client hook
│   │   ├── stores/                  # Zustand state management
│   │   └── types/                   # TypeScript type definitions
│   ├── package.json
│   └── next.config.js
│
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.dashboard
├── railway.toml
├── .env.example
└── README.md
```

[↑ Back to Top](#table-of-contents)

## 16. Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend framework | FastAPI | Async-native, auto-generated OpenAPI docs, fast enough for <100ms pipeline |
| Database | SQLite | Zero-config, single-file, sufficient for hackathon scale, hash chain integrity |
| Cache/state | Redis | Pub/sub for real-time dashboard, sorted sets for escalation queue, fast rate limiting |
| DSL parser | PEG (parsimonious) | Composable grammars, good error messages, Python-native |
| Crypto | Ed25519 (PyNaCl) | Fast signing/verification, compact keys, well-suited for agent identity |
| Hash chain | SHA-256 | Industry standard, fast, sufficient for tamper detection |
| Dashboard | Next.js + React | SSR for initial load, rich component ecosystem, Vercel-native deployment |
| Charts | Recharts + D3 | Recharts for standard charts, D3 for kill chain graph and DFA visualization |
| MCP transport | stdio + SSE | Standard MCP transports, SSE for cloud deployment |
| Semantic grounding | Deterministic (no LLM) | Critical design principle: validation layer must not depend on the thing being validated |
| Knowledge graph storage | SQLite JSON + optional Neo4j | JSON columns for hackathon simplicity, Neo4j adapter for enterprise |
| LLM evaluation | Automated benchmarks | Systematic, repeatable, auditable — not ad-hoc manual testing |
| Deployment | Railway + Vercel + Docker | Railway for backend (Redis addon), Vercel for static dashboard, Docker for offline |

[↑ Back to Top](#table-of-contents)

## 17. Acceptance Criteria Traceability

| Requirement | Key Design Components |
|-------------|----------------------|
| R1: Zero Trust Identity | `identity.py`, `trust_engine.py`, Ed25519 keys, CapabilityToken model |
| R2: DSL | `dsl_parser.py`, `dsl_printer.py`, PEG grammar, LTL operators |
| R3: Threat Detection | `threat/` package, AttackChainAnalyzer, STAC defense |
| R4: DPDP Compliance | `compliance/` package, PII_Masker regex patterns |
| R5: Eval Pipeline | `pipeline.py` — 10-stage pipeline with short-circuit |
| R6: Audit Trail | `audit/` package, SQLite hash chain, Evidence_Package |
| R7: Multi-Agent | `multi_agent/` package, delegation chain, collusion detection |
| R8: Escalation | `EscalationManager`, Redis sorted set queue, SOC_Dashboard |
| R9: SOC Dashboard | `dashboard/` React app, WebSocket real-time feed |
| R10: Law Enforcement | `cert_in.py`, Evidence_Package, Incident_Report |
| R11: SDK & API | `api/` routes, Framework_Adapters |
| R12: Infrastructure | FastAPI, Redis, SQLite, CORS config |
| R13: Demo Scenario | `demo/` package, pre-configured attack sequence |
| R14: Formal Verification | `formal_verifier.py`, verification certificates |
| R15: DFA Modeling | `dfa_engine.py`, DFA_Behavioral_Model, state diagram viz |
| R16: Trust Scoring | `trust_engine.py`, Redis trust cache, graduated enforcement |
| R17: Determinism | `replay.py`, Determinism_Report, batch audit replay |
| R18: MCP Proxy | `mcp/proxy.py`, Tool_Call_Intercept, Tool_Discovery_Filter |
| R19: MCP Safety Server | `mcp/safety_server.py`, 5 safety tools |
| R20: Deployment | Docker Compose, Railway config, Vercel config |
| R21: LLM Gateway | `llm/gateway.py`, providers, fallback chains |
| R22: Ethics | `ethics/` package, India-specific bias categories |
| R23: Hallucination | `Hallucination_Detector`, tool receipt verification |
| R24: Seven Sutras | `seven_sutras.py`, radar chart, compliance reports |
| R25: LLM Cost | `llm/budget.py`, Redis budget counters |
| R26: Explainability | `explain/` package, 3-layer Decision_Explanation |
| R27: Model Transparency | Model_Card, Model_Provenance_Record, Model Registry |
| R28: LLM Observability | `llm/observability.py`, drift detection, baseline comparison |
| R29: Multi-Tenant | tenant_id on all models, Tenant_Isolation, scoped queries |
| R30: LLM Evaluation | `llm/eval_engine.py`, `llm/red_team.py`, Safety_Benchmarks |
| R31: Semantic Grounding | `grounding/` package, Knowledge_Graph, Deterministic_Validator |

[↑ Back to Top](#table-of-contents)

## 18. Correctness Properties

### Property 1: DSL Round-Trip (R2.7)
- Type: Round-trip
- Description: For all valid KavachAI DSL source texts, parsing then printing then parsing produces an equivalent AST.
- Test: `parse(print(parse(source))) == parse(source)` for randomly generated valid DSL programs.

### Property 2: Hash Chain Integrity (R6.2)
- Type: Invariant
- Description: For any sequence of audit entries appended to the trail, recomputing the hash chain from the first entry produces hashes matching all stored entry_hash values.
- Test: Append N random audit entries, then verify the chain by recomputing SHA-256 from entry 1 to N.

### Property 3: Monotonic Sequence Numbers (R6.8)
- Type: Invariant
- Description: Within any session, audit entry sequence numbers are strictly monotonically increasing with no gaps.
- Test: For any sequence of appended entries in a session, `entries[i+1].sequence_number == entries[i].sequence_number + 1`.

### Property 4: Trust Score Bounds (R16.1, R16.4)
- Type: Invariant
- Description: For any sequence of ALLOW/BLOCK/QUARANTINE verdicts applied to an agent, the trust score remains in [0.0, 1.0] and the trust level classification matches the defined ranges.
- Test: Apply random sequences of verdicts, verify `0.0 <= trust_score <= 1.0` and level matches score range.

### Property 5: PII Masking Completeness (R4.4)
- Type: Metamorphic
- Description: For any string containing Aadhaar, PAN, or mobile number patterns, the masked output contains zero instances of the original PII values.
- Test: Generate strings with embedded PII patterns, mask them, verify no original PII remains via regex search.

### Property 6: Pipeline Short-Circuit (R5.2, R5.3)
- Type: Invariant
- Description: When any pipeline stage returns BLOCK/ESCALATE/QUARANTINE, no subsequent stage executes and the final verdict matches the blocking stage's verdict.
- Test: Inject blocking verdicts at each stage position, verify subsequent stages have zero invocations.

### Property 7: Grounding Score Bounds (R31.4)
- Type: Invariant
- Description: For any set of claims verified by the Semantic Grounding Layer, the grounding score is always in [0.0, 1.0] and equals grounded_claims / total_claims.
- Test: Generate random claim sets with varying grounded/ungrounded ratios, verify score computation.

### Property 8: Model Safety Score Aggregation (R30.2)
- Type: Invariant
- Description: The overall Model_Safety_Score is always in [0, 100] and equals the weighted sum of sub-scores according to benchmark weights.
- Test: Generate random sub-scores and weights, verify overall = sum(sub_score * weight) and 0 <= overall <= 100.

### Property 9: Schema Enforcement Idempotence (R31.3)
- Type: Idempotence
- Description: Validating the same output against the same schema always produces the same result, regardless of how many times validation is run.
- Test: `validate(output, schema) == validate(output, schema)` for randomly generated outputs and schemas.

### Property 10: Threat Score Aggregation Bounds (R3.8)
- Type: Invariant
- Description: Session-level threat score computed by weighted decay aggregation is always in [0.0, 1.0], and more recent actions contribute more weight.
- Test: Generate random action threat scores, verify session score in bounds and that swapping a recent high-threat action with an older one changes the score.

### Property 11: Capability Token Scope Enforcement (R1.4, R1.5)
- Type: Invariant
- Description: An agent can never successfully invoke a tool not listed in its active Capability_Token. For any tool call outside scope, the verdict is always BLOCK with PRIVILEGE_VIOLATION.
- Test: Generate random capability tokens and tool calls, verify out-of-scope calls always produce BLOCK.

### Property 12: Deterministic Validator Consistency (R31.7)
- Type: Idempotence
- Description: The Deterministic_Validator produces identical results for identical inputs across multiple invocations — no randomness, no LLM dependency.
- Test: Run validator on same input 100 times, verify all results are identical.

[↑ Back to Top](#table-of-contents)
