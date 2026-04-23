# KavachAI Tutorial — Getting Started Guide

> A step-by-step guide for first-time users. By the end of this tutorial, you'll understand what KavachAI does, how it works, and how to use every major feature.

---

## Table of Contents

1. [What is KavachAI?](#1-what-is-kavachai)
2. [Key Concepts](#2-key-concepts)
3. [Installation & Setup](#3-installation--setup)
4. [Running the Demo](#4-running-the-demo)
5. [Understanding the Evaluation Pipeline](#5-understanding-the-evaluation-pipeline)
6. [Writing Safety Policies (KavachAI DSL)](#6-writing-safety-policies-kavachai-dsl)
7. [Using the REST API](#7-using-the-rest-api)
8. [Using the SOC Dashboard](#8-using-the-soc-dashboard)
9. [MCP Proxy Gateway](#9-mcp-proxy-gateway)
10. [Compliance & Governance](#10-compliance--governance)
11. [Advanced Features](#11-advanced-features)
12. [Architecture Overview](#12-architecture-overview)

---

## 1. What is KavachAI?

Imagine you have an AI agent — maybe a customer service bot, a coding assistant, or a financial advisor. This agent can call tools: look up customer data, send emails, process payments, call APIs.

**The problem:** How do you make sure the agent doesn't do something dangerous? What if someone tricks it with a prompt injection? What if it tries to exfiltrate sensitive data? What if it escalates its own privileges?

**KavachAI is the answer.** It sits between your AI agent and its tools like a security firewall. Every single tool call passes through KavachAI's 10-stage evaluation pipeline before it's allowed to execute.

```
Your AI Agent  ──►  KavachAI Firewall  ──►  Tools (APIs, databases, etc.)
                         │
                    10-stage check:
                    ✓ Identity verified?
                    ✓ Has permission?
                    ✓ Policy allows it?
                    ✓ Threat detected?
                    ✓ PII protected?
                    ✓ Ethically sound?
                         │
                    ALLOW / BLOCK / ESCALATE
```

Think of it as a **Zero Trust security guard** for AI agents. No action is trusted by default — every single one must prove it's safe.

---

## 2. Key Concepts

Before diving in, let's understand the building blocks. Each concept builds on the previous one.

### 2.1 Agent Identity

Every AI agent that interacts with KavachAI gets a **cryptographic identity** — an Ed25519 key pair (like a digital passport). This means:

- Each agent has a unique ID
- Every action the agent takes is cryptographically signed
- You can always prove which agent did what
- Agents can be revoked instantly if compromised

```
Agent "financial-bot"
├── agent_id: "a1b2c3..."
├── public_key: (Ed25519, used to verify signatures)
├── trust_score: 0.85 (dynamic, changes over time)
└── trust_level: TRUSTED (derived from score)
```

### 2.2 Capability Tokens

An agent's identity alone doesn't grant access. Agents also need a **Capability Token** — a signed, time-limited permission slip that says exactly which tools they can use.

```
Capability Token for "financial-bot"
├── allowed_tools: ["verify_identity", "customer_lookup", "payment_process"]
├── expires_at: 2026-03-30T10:00:00Z
└── signature: (signed by KavachAI's system key)
```

If an agent tries to call a tool not in its token (like `admin_panel`), KavachAI immediately blocks it. No exceptions.

### 2.3 Trust Levels

Every agent has a dynamic **trust score** (0.0 to 1.0) that changes based on behavior:

| Trust Level | Score Range | What It Means |
|-------------|-------------|---------------|
| TRUSTED | 0.8 – 1.0 | Full access within capability scope |
| STANDARD | 0.5 – 0.79 | Normal access, some restrictions |
| RESTRICTED | 0.2 – 0.49 | Limited access, extra scrutiny |
| QUARANTINED | 0.0 – 0.19 | Session suspended, all actions blocked |

Good behavior slowly increases trust. Violations decrease it. A critical violation can drop an agent from TRUSTED to QUARANTINED in one action.

### 2.4 The Evaluation Pipeline

This is the heart of KavachAI. Every tool call passes through **10 stages** in sequence:

```
1. Authentication     → Is this a known, non-revoked agent?
2. Capability Token   → Does the agent have permission for this tool?
3. DSL Policy         → Do the safety policies allow this action?
4. Threat Detection   → Is this a prompt injection, privilege escalation, etc.?
5. DPDP Compliance    → Does this comply with India's data protection law?
6. Ethics Check       → Is this biased, toxic, or unfair?
7. PII Masking        → Does the output contain Aadhaar, PAN, or phone numbers?
8. LLM Reasoning      → Capture the agent's chain-of-thought for audit
9. Semantic Grounding  → Are the agent's claims factually grounded?
10. Attestation       → Sign and record the verdict in the audit trail
```

**Short-circuit rule:** If any stage returns BLOCK, ESCALATE, or QUARANTINE, the pipeline stops immediately. No subsequent stages run.

### 2.5 Verdicts

Every evaluation produces one of five verdicts:

| Verdict | Meaning | What Happens |
|---------|---------|-------------|
| **ALLOW** | Safe to proceed | Tool call is forwarded to the actual tool |
| **BLOCK** | Denied | Tool call is rejected with an error |
| **FLAG** | Permitted with warning | Tool call proceeds, but a warning is logged |
| **ESCALATE** | Needs human review | Tool call is held until a human operator approves/rejects |
| **QUARANTINE** | Critical threat | Tool call blocked, entire session suspended |

### 2.6 The KavachAI DSL

KavachAI has its own policy language — a Domain-Specific Language (DSL) — for writing safety rules. Each rule follows a simple pattern:

```
rule <name> {
  when <trigger>       ← What event triggers this rule?
  check <predicate>    ← What condition must be true?
  then <action>        ← What should KavachAI do?
}
```

We'll cover this in detail in [Section 6](#6-writing-safety-policies-kavachai-dsl).

### 2.7 Audit Trail

Every single action — allowed or blocked — is recorded in a **cryptographic audit trail**. Each entry is linked to the previous one via SHA-256 hashes (like a blockchain). This means:

- You can't delete or modify entries without breaking the chain
- You can prove the complete history of any session
- Evidence packages can be exported for forensic investigation or legal proceedings

### 2.8 Kill Chains

When KavachAI detects a sequence of suspicious actions, it builds a **kill chain** — a visualization of the attack progression:

```
Reconnaissance → Delivery → Exploitation → Exfiltration
(customer_lookup) → (external_api) → (admin_panel) → (send_email)
```

It also detects **STAC attacks** (Sequential Tool Attack Chains) — where each individual action looks harmless, but the sequence together forms an attack.

---

## 3. Installation & Setup

### Prerequisites

- Python 3.11+ (`py --version` on Windows, `python3 --version` on Mac/Linux)
- Node.js 18+ (for the dashboard)
- Redis (optional — for real-time features)

### Step 1: Clone the Repository

```bash
git clone https://gitlab.com/sanchayan1/kavachai.git
cd kavachai
```

### Step 2: Install Backend Dependencies

```bash
# Windows
py -m pip install -r kavachai/backend/requirements.txt

# Mac/Linux
pip install -r kavachai/backend/requirements.txt
```

### Step 3: Install Dashboard Dependencies

```bash
cd kavachai/dashboard
npm install
cd ../..
```

### Step 4: Start the Backend

```bash
# Windows
py -m uvicorn kavachai.backend.main:app --reload --port 8000

# Mac/Linux
uvicorn kavachai.backend.main:app --reload --port 8000
```

The API is now running at `http://localhost:8000`. Check it:

```bash
curl http://localhost:8000/health
# → {"status":"ok","service":"kavachai","version":"0.1.0"}
```

### Step 5: Start the Dashboard

```bash
cd kavachai/dashboard
npm run dev
```

The SOC Dashboard is now at `http://localhost:3000`.

### Docker Alternative

If you prefer Docker, just run:

```bash
docker-compose up
```

This starts the backend (port 8000), Redis (port 6379), and everything is pre-configured.

---

## 4. Running the Demo

The fastest way to see KavachAI in action is the built-in demo. It simulates a 5-stage financial services attack and shows how KavachAI catches every stage.

```bash
# Windows
py kavachai/backend/demo/run_demo.py

# Mac/Linux
python kavachai/backend/demo/run_demo.py
```

You'll see output like this:

```
======================================================================
  KavachAI — Zero Trust Safety Firewall Demo
  5-Stage Financial Services Attack Scenario
======================================================================

Stage 1: Indirect Prompt Injection
  Tool:    customer_lookup
  Verdict: 🔴 QUARANTINE
  Threat:  0.95
  Reason:  High threat score: 0.95

Stage 2: Aadhaar Exfiltration Attempt
  Tool:    send_email
  Verdict: 🔴 QUARANTINE
  Reason:  Rule prevent_aadhaar_exfiltration matched

Stage 3: Privilege Escalation
  Tool:    admin_panel
  Verdict: 🛑 BLOCK
  Reason:  Tool 'admin_panel' not in capability scope

Stage 4: Covert Data Channel
  Tool:    send_email
  Verdict: 🔴 QUARANTINE
  Reason:  Rule prevent_aadhaar_exfiltration matched

Stage 5: STAC Sequential Attack Chain
  Tool:    payment_process
  Verdict: 🔶 ESCALATE
  Reason:  Rule block_unauthorized_payment matched

Summary: 5/5 attack stages detected and blocked/escalated
```

### What the Demo Does

| Stage | Attack Type | How KavachAI Catches It |
|-------|------------|------------------------|
| 1 | Prompt injection hidden in a customer message | Threat detector finds "ignore previous instructions" pattern (score: 0.95) |
| 2 | Trying to email Aadhaar numbers externally | DSL policy `prevent_aadhaar_exfiltration` triggers on data flow to external |
| 3 | Attempting to access admin panel | Capability token doesn't include `admin_panel` — instant BLOCK |
| 4 | Base64-encoding sensitive data in an email | Same exfiltration policy catches the data flow pattern |
| 5 | Chain of benign calls leading to unauthorized payment | DSL policy catches payment > ₹50,000 by non-trusted agent |

---

## 5. Understanding the Evaluation Pipeline

Let's trace a single action through the pipeline to see exactly what happens.

### Example: An agent tries to process a ₹75,000 payment

```python
ActionRequest(
    agent_id="agent-001",
    tool_name="payment_process",
    parameters={"amount": 75000, "to": "external-account"},
    session_id="sess-001",
)
```

**Stage 1 — Authentication:** Is `agent-001` registered and not revoked? ✅ Yes.

**Stage 2 — Capability Token:** Does the agent's token include `payment_process`? ✅ Yes.

**Stage 3 — DSL Policy:** The policy engine checks all loaded rules. Rule `block_unauthorized_payment` triggers:
- Trigger matches: `tool_call("payment_process")` ✅
- Predicate matches: `amount > 50000` (75000 > 50000) ✅ AND `trust_level != "trusted"` ✅
- Enforcement: `escalate severity critical`

**Result:** Pipeline short-circuits. Stages 4-10 don't run. Verdict: **ESCALATE**.

The action is held in the escalation queue until a human operator approves or rejects it.

---

## 6. Writing Safety Policies (KavachAI DSL)

The DSL is how you tell KavachAI what's allowed and what isn't. Let's learn it step by step.

### 6.1 Basic Structure

Every policy file starts with a header:

```
policy my_safety_rules
version "1.0"
description "Safety rules for my application"
```

### 6.2 Your First Rule

```
rule block_dangerous_deletes {
  when tool_call("delete_user")
  check agent.trust_level != "trusted"
  then block severity high
}
```

This says: "When any agent tries to call `delete_user`, check if they're not TRUSTED. If so, block it."

### 6.3 Triggers

Triggers define **when** a rule activates:

```
# Match a specific tool
when tool_call("payment_process")

# Match multiple tools
when tool_call("send_email" | "external_api" | "webhook")

# Match with wildcards
when tool_call("admin_*")

# Match ALL tool calls (using LTL "always" operator)
when always(tool_call("*"))
```

### 6.4 Predicates

Predicates define **what condition** must be true:

```
# Compare a parameter value
check action.params.amount > 50000

# Check agent trust level
check agent.trust_level != "trusted"

# Combine with AND/OR
check action.params.amount > 50000
  and agent.trust_level != "trusted"

# Temporal: was another tool called recently?
check within 5m of tool_call("external_api")

# Data flow: is data moving from internal to external?
check data_from "customer_records" reaches "external"

# PII detection
check output contains_pii("aadhaar" | "pan" | "mobile")
```

### 6.5 Enforcement Actions

```
then allow                    # Explicitly permit
then block severity high      # Deny the action
then flag severity medium     # Allow but log a warning
then escalate severity critical  # Hold for human review
then quarantine severity critical  # Block and suspend session
```

### 6.6 Workflows (DFA Behavioral Models)

You can define expected agent behavior as a state machine:

```
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
```

If an agent reaches the `dangerous` state (`admin_access`), KavachAI raises an alert. If an agent tries a transition that doesn't exist in the workflow, it's flagged as anomalous.

### 6.7 Ethics Constructs

```
ensure fairness in loan_processing for all demographic_groups
```

This tells KavachAI to monitor the `loan_processing` context for bias across demographic groups.

### 6.8 Uploading Policies via API

```bash
curl -X PUT http://localhost:8000/api/v1/policies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_safety_rules",
    "dsl_source": "policy my_rules\nversion \"1.0\"\n\nrule block_admin {\n  when tool_call(\"admin_*\")\n  check agent.trust_level != \"trusted\"\n  then block severity high\n}",
    "tenant_id": "default"
  }'
```

---

## 7. Using the REST API

### 7.1 Register an Agent

```bash
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo" \
  -d '{
    "name": "my-agent",
    "capability_scope": ["search", "send_email"],
    "tenant_id": "default"
  }'
```

Response:
```json
{
  "agent_id": "abc-123...",
  "public_key": "base64...",
  "private_key": "base64...",
  "capability_token_id": "tok-456..."
}
```

Save the `agent_id` and `private_key` — you'll need them.

### 7.2 Evaluate an Action

```bash
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo" \
  -d '{
    "request_id": "req-001",
    "agent_id": "abc-123...",
    "session_id": "sess-001",
    "tool_name": "send_email",
    "parameters": {"to": "user@example.com", "body": "Hello"},
    "tenant_id": "default"
  }'
```

Response:
```json
{
  "verdict": "allow",
  "reason": "All checks passed",
  "matched_policies": [],
  "threat_score": 0.0,
  "ethics_score": 0.0,
  "attestation": { "attestation_id": "att-789...", ... }
}
```

### 7.3 View Audit Trail

```bash
curl http://localhost:8000/api/v1/sessions/sess-001/audit-trail \
  -H "X-API-Key: demo"
```

### 7.4 Check Compliance Status

```bash
# DPDP Act compliance (India)
curl http://localhost:8000/api/v1/compliance/dpdp-status

# India AI Seven Sutras
curl http://localhost:8000/api/v1/compliance/seven-sutras

# GDPR compliance (EU)
curl http://localhost:8000/api/v1/compliance/gdpr-status

# UK FCA/PRA compliance
curl http://localhost:8000/api/v1/compliance/fca-pra-status
```

### 7.5 Manage Escalations

```bash
# List pending escalations
curl http://localhost:8000/api/v1/escalations

# Approve an escalation
curl -X POST http://localhost:8000/api/v1/escalations/esc-001/resolve \
  -H "Content-Type: application/json" \
  -d '{"decision": "approve", "operator_id": "admin-1", "reason": "Verified legitimate"}'
```

---

## 8. Using the SOC Dashboard

The dashboard is your real-time command center. Here's what each page does:

### Threat Feed (Home Page)
The main monitoring view. Shows all active sessions sorted by threat score, with real-time alerts for quarantines and escalations. The stats row gives you an instant overview of active sessions, detected threats, quarantined sessions, and pending escalations.

### Kill Chains
Visualizes multi-stage attack progressions. Each node represents an attack stage (reconnaissance, delivery, exploitation, exfiltration). STAC attacks are highlighted with a red badge. Click any stage to see the full action details.

### Escalations
Your action queue. When KavachAI escalates an action for human review, it appears here with the threat score, reason, and full context. You can approve or reject each escalation directly from this page.

### Forensics
Step-by-step replay of any session. Select an action from the timeline to see the 3-layer decision explanation:
- **LLM Reasoning:** The agent's chain-of-thought (if captured)
- **Policy Evaluation:** Which rules matched and why
- **User-Facing Summary:** Plain-language explanation of the decision

The hash chain indicator at the top confirms audit trail integrity.

### Compliance
Four panels covering multi-jurisdiction compliance:
- **DPDP Act 2023 (India):** Consent coverage, PII masking rate, data localization status
- **GDPR (EU):** Lawful basis coverage, right to erasure requests, breach notification status, cross-border transfer compliance
- **UK FCA/PRA:** Consumer Duty status, SS1/23 model risk, SM&CR accountability mapping
- **Seven Sutras:** Radar chart showing compliance with India's AI governance principles (Trust, People First, Innovation, Fairness, Accountability, Understandable, Safety)

### Agents
Table of all registered agents with their trust scores, trust levels, capability scopes, and status. Useful for monitoring which agents are healthy and which are restricted or quarantined.

### Policies
View and manage loaded DSL policies. The right panel shows the policy source code with syntax highlighting. Use this to verify which rules are active.

### Model Eval
Safety scores for each LLM model across 5 dimensions (prompt injection resistance, toxicity, bias, hallucination, accuracy). Also shows red team results — how many vulnerabilities were found during adversarial testing.

### LLM Usage
Cost tracking dashboard. Shows total tokens used, total cost, budget utilization, and per-model health metrics (latency, error rate, refusal rate).

### Grounding
Semantic grounding reports. Shows which agent claims are backed by knowledge graph data, tool responses, or domain ontologies — and which claims are ungrounded (potential hallucinations).

---

## 9. MCP Proxy Gateway

KavachAI works as a transparent **MCP (Model Context Protocol) proxy**. This means any MCP-compatible agent can use KavachAI without code changes.

### How It Works

```
Your Agent (Claude, GPT, LangChain, CrewAI)
    │
    │  MCP protocol (stdio or SSE)
    ▼
KavachAI MCP Proxy Gateway (port 3001)
    │
    │  1. Intercept tool call
    │  2. Run evaluation pipeline
    │  3. ALLOW → forward to real tool
    │     BLOCK → return error
    │     ESCALATE → hold for human
    │
    ▼
Actual MCP Tool Servers (file system, database, APIs)
```

### MCP Safety Server

KavachAI also exposes 5 safety tools that agents can call directly:

| Tool | What It Does |
|------|-------------|
| `check_policy` | Dry-run: "Would this action be allowed?" (without recording in audit) |
| `get_my_permissions` | "What tools can I use? What's my trust level?" |
| `request_escalation` | "I'm unsure about this action — please have a human review it" |
| `get_compliance_status` | "What's the current DPDP compliance posture?" |
| `report_suspicious_input` | "I received suspicious input — flagging it for review" |

This lets safety-aware agents proactively check permissions and report threats.

---

## 10. Compliance & Governance

KavachAI is a **jurisdiction-aware, multi-jurisdiction compliance framework**. Tenants can configure which jurisdictions apply to them (India, EU, UK, or any combination). All compliance engines run in parallel during the evaluation pipeline.

### 10.1 DPDP Act 2023 (India's Data Protection Law)

KavachAI enforces:
- **PII Masking:** Automatically detects and masks Aadhaar numbers (→ `XXXX XXXX 1234`), PAN cards, Indian mobile numbers, UPI IDs, and email addresses
- **Consent Verification:** Checks that data processing has valid consent records
- **Data Localization:** Enforces that data stays within configured boundaries
- **Breach Notification:** Triggers alerts when potential data breaches are detected

### 10.2 India AI Seven Sutras

KavachAI maps its capabilities to India's 7 AI governance principles. The Seven Sutras engine is part of the broader multi-jurisdiction compliance framework and can be used alongside GDPR and FCA/PRA compliance.

| Sutra | KavachAI Feature |
|-------|-----------------|
| Trust | Cryptographic audit trail, hash chain integrity |
| People First | PII masking, DPDP compliance, consent management |
| Innovation | Semantic grounding, knowledge graph validation |
| Fairness | Bias detection (gender, caste, religion, regional, socioeconomic) |
| Accountability | Audit trail, evidence packages, CERT-In reporting |
| Understandable | 3-layer decision explanations (LLM, policy, user-facing) |
| Safety | Threat detection, policy engine, kill chain analysis |

### 10.3 CERT-In Reporting

For serious incidents, KavachAI can generate structured incident reports in CERT-In format, complete with cryptographically signed evidence packages suitable for law enforcement.

### 10.4 GDPR (EU General Data Protection Regulation)

KavachAI provides a dedicated GDPR compliance engine covering:

- **Lawful Basis Tracking:** Records and verifies the lawful basis for every data processing activity (consent, legitimate interest, contract, legal obligation, vital interest, public task)
- **Right to Erasure:** Tracks "right to be forgotten" requests and ensures data subjects can request deletion of their personal data
- **Data Portability:** Supports data export in machine-readable formats for data subject access requests (DSARs)
- **72-Hour Breach Notification:** Monitors breach detection timestamps and alerts when the 72-hour notification window to the supervisory authority is approaching
- **Data Protection Impact Assessment (DPIA):** Tracks DPIA status for high-risk processing activities
- **Cross-Border Transfer Controls:** Validates that international data transfers have appropriate safeguards — adequacy decisions, Standard Contractual Clauses (SCCs), or Binding Corporate Rules (BCRs)
- **PII Detection (EU):** Detects and masks EU-specific PII patterns including IBAN, EU national IDs, and EU/UK phone numbers

```bash
# Check GDPR compliance status
curl http://localhost:8000/api/v1/compliance/gdpr-status
```

### 10.5 EU AI Act (2024/1689)

KavachAI maps to the EU AI Act requirements:

- **Risk Classification:** AI systems are classified as unacceptable, high, limited, or minimal risk
- **Transparency Obligations:** 3-layer decision explanations (LLM reasoning, policy evaluation, user-facing summary) satisfy the right-to-explanation requirement
- **Conformity Assessments:** For high-risk AI systems, KavachAI provides audit trails and evidence packages that support conformity assessment documentation
- **Human Oversight:** The escalation queue ensures human-in-the-loop review for high-risk decisions

### 10.6 UK FCA & PRA Compliance

KavachAI includes a dedicated engine for UK financial regulatory compliance:

- **FCA Consumer Duty:** Tracks compliance with the FCA's Consumer Duty requirements — ensuring AI systems treat customers fairly and deliver good outcomes
- **PRA SS1/23 Model Risk Management:** Monitors model risk management status including model validation, ongoing monitoring, and documentation requirements
- **SM&CR Accountability:** Maps which Senior Manager is responsible for each AI system, ensuring clear individual accountability for AI decisions
- **DORA ICT Risk Management:** Tracks ICT risk management status for EU/UK financial entities, including incident reporting and third-party risk
- **MiFID II Controls:** Monitors algorithmic trading controls, best execution obligations, and transaction reporting requirements

```bash
# Check UK FCA/PRA compliance status
curl http://localhost:8000/api/v1/compliance/fca-pra-status
```

### 10.7 Multi-Jurisdiction PII Masking

KavachAI's PII masker supports patterns across all jurisdictions:

| Jurisdiction | PII Patterns |
|-------------|-------------|
| India | Aadhaar (12-digit), PAN (ABCDE1234F), Indian mobile (+91), UPI ID |
| EU/UK | IBAN, UK National Insurance Number (AB123456C), UK Sort Code, EU/UK phone numbers (+44, +33, +49), Passport numbers |
| Global | Email addresses |

All PII patterns are applied simultaneously — a single text can have Indian, EU, and UK PII detected and masked in one pass.

---

## 11. Advanced Features

### Multi-Agent Governance
When multiple agents work together, KavachAI enforces:
- **Delegation chain depth limits** (default: max 3 levels deep)
- **Privilege amplification prevention** (Agent B can't get more permissions than Agent A gave it)
- **Collusion detection** (detects coordinated policy circumvention across agents)

### Hallucination Detection
Compares agent claims against actual tool attestation records:
- **TOOL_FABRICATION:** Agent claims to have called a tool it never called
- **RESULT_MISSTATEMENT:** Agent states values that differ from actual tool responses
- **UNGROUNDED:** Claims not backed by any knowledge source

### Formal Policy Verification
Before activating a policy, you can verify it:
- **Consistency:** No conflicting rules (e.g., same trigger with both ALLOW and BLOCK)
- **Completeness:** All known tools are covered by at least one rule

```bash
curl -X POST http://localhost:8000/api/v1/policies/pol-001/verify
```

### Session Replay
Re-execute a session's action sequence to verify determinism:

```bash
curl -X POST http://localhost:8000/api/v1/sessions/sess-001/replay
```

### LLM Evaluation & Red Teaming
Before deploying a new LLM model, evaluate its safety:

```bash
# Run safety benchmarks
curl -X POST http://localhost:8000/api/v1/llm/evaluate/gpt-4

# Run adversarial red team testing
curl -X POST http://localhost:8000/api/v1/llm/red-team/gpt-4
```

Models scoring below 70/100 are automatically blocked from the LLM gateway.

---

## 12. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SOC Dashboard (React/Next.js)             │
│  Threat Feed │ Kill Chains │ Escalations │ Forensics │ ...  │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST + WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│                  KavachAI Backend (FastAPI)                   │
│                                                              │
│  ┌─────────── Zero Trust Evaluation Pipeline ─────────────┐ │
│  │ Auth → Token → Policy → Threat → DPDP → Ethics →      │ │
│  │ PII → Reasoning → Grounding → Attestation              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │ DSL Policy │ │ Threat     │ │ Ethics     │              │
│  │ Engine     │ │ Detector   │ │ Engine     │              │
│  ├────────────┤ ├────────────┤ ├────────────┤              │
│  │ Trust      │ │ Audit      │ │ Grounding  │              │
│  │ Engine     │ │ Trail      │ │ Layer      │              │
│  ├────────────┤ ├────────────┤ ├────────────┤              │
│  │ LLM        │ │ MCP Proxy  │ │ Multi-Agent│              │
│  │ Gateway    │ │ Gateway    │ │ Governor   │              │
│  └────────────┘ └────────────┘ └────────────┘              │
└──────────┬──────────────────────────┬───────────────────────┘
           │                          │
    ┌──────▼──────┐            ┌──────▼──────┐
    │   Redis     │            │   SQLite    │
    │ (real-time) │            │ (audit/     │
    │             │            │  persistent)│
    └─────────────┘            └─────────────┘
```

### Backend Packages

| Package | Purpose |
|---------|---------|
| `core/` | Pipeline, policy engine, DSL parser, identity, trust, DFA, escalation, tenant management |
| `threat/` | Prompt injection, tool poisoning, privilege escalation, covert channels, attack chains |
| `audit/` | Hash chain, audit trail, evidence packages, session replay |
| `compliance/` | PII masking, DPDP engine, Seven Sutras, CERT-In reporting |
| `ethics/` | Bias detection, toxicity filtering, ethics engine |
| `explain/` | Reasoning capture, 3-layer decision explanations |
| `grounding/` | Semantic grounding, hallucination detection |
| `llm/` | LLM gateway, evaluation engine, red teaming, observability |
| `mcp/` | MCP proxy gateway, safety server, transport |
| `multi_agent/` | Multi-agent governor, delegation chains, collusion detection |
| `demo/` | Demo scenario, sample policies, knowledge graphs |
| `api/` | REST API routes, WebSocket endpoint |

---

## What's Next?

- **Customize policies:** Write your own `.shield` files for your specific use case
- **Integrate your agent:** Point your MCP-compatible agent at KavachAI's proxy (port 3001)
- **Deploy:** Use `docker-compose up` for local deployment or Railway for cloud
- **Monitor:** Keep the SOC Dashboard open to watch threats in real time

For the full technical specification, see [specs/design.md](../specs/design.md). For requirements and acceptance criteria, see [specs/requirements.md](../specs/requirements.md).
