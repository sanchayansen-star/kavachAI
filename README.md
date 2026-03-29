# KavachAI (कवच) — Zero Trust Safety Firewall for Agentic AI

> A production-grade governance platform for autonomous AI agents, built for the ISB Hackathon on Cybersecurity & AI Safety 2025-26.

**Kavach** (कवच) means "armor" or "protective shield" in Sanskrit — reflecting the system's role as a protective governance layer for autonomous AI agents.

---

## What is KavachAI?

KavachAI is a Zero Trust safety firewall that sits between AI agents and their tools, enforcing safety policies, detecting threats, ensuring regulatory compliance, and providing tamper-proof audit trails — all in real time.

It operates as an **MCP Proxy Gateway**, transparently intercepting all tool calls between any MCP-compatible agent (Claude, GPT, LangChain, CrewAI) and any MCP server (tools), running a 10-stage evaluation pipeline before allowing actions to execute.

```
Your AI Agent  ──►  KavachAI Firewall  ──►  Tools (APIs, databases, etc.)
                         │
                    10-stage pipeline:
                    ✓ Identity  ✓ Capability Token
                    ✓ DSL Policy  ✓ Threat Detection
                    ✓ DPDP Compliance  ✓ Ethics
                    ✓ PII Masking  ✓ LLM Reasoning
                    ✓ Semantic Grounding  ✓ Attestation
                         │
                    ALLOW / BLOCK / ESCALATE / QUARANTINE
```

## Key Capabilities

| Capability | Description | Status |
|-----------|-------------|--------|
| Zero Trust Identity | Ed25519 cryptographic agent identities with scoped capability tokens | ✅ Implemented |
| KavachAI DSL | Formal policy language with LTL temporal logic and DFA behavioral modeling | ✅ Implemented |
| Threat Detection | Prompt injection, STAC attacks, privilege escalation, covert channels, kill chain analysis | ✅ Implemented |
| MCP Proxy Gateway | Protocol-native governance for any MCP-compatible agent and tool | ✅ Implemented |
| Multi-LLM Gateway | Unified routing with safety governance and budget enforcement | ✅ Implemented |
| Semantic Grounding | Deterministic validation against knowledge graphs and domain ontologies | ✅ Implemented |
| Hallucination Detection | Compare agent claims against attestation records, detect fabrication/misstatement | ✅ Implemented |
| AI Ethics Engine | India-specific bias detection (gender, caste, religion, regional), toxicity filtering | ✅ Implemented |
| DPDP Act Compliance | Aadhaar/PAN masking, consent verification, data localization, breach notification | ✅ Implemented |
| Seven Sutras Compliance | Full mapping to India's AI Governance Guidelines 2025 | ✅ Implemented |
| Cryptographic Audit Trail | SHA-256 hash chains, evidence packages, session replay, CERT-In reporting | ✅ Implemented |
| SOC Dashboard | 10-page real-time dashboard: threats, kill chains, escalations, forensics, compliance | ✅ Implemented |
| LLM Evaluation | Automated safety benchmarking and red-teaming before model deployment | ✅ Implemented |
| LLM Explainability | 3-layer decision explanations (LLM reasoning, policy, user-facing) in English & Hindi | ✅ Implemented |
| Multi-Agent Governance | Delegation chain limits, privilege amplification prevention, collusion detection | ✅ Implemented |
| Formal Policy Verification | Consistency and completeness checking for DSL policies | ✅ Implemented |
| Multi-Tenant Isolation | Tenant-scoped API keys, rate limits, data isolation | ✅ Implemented |

## Quick Start

### Run the Demo (Fastest Way)

```bash
git clone https://gitlab.com/sanchayan1/kavachai.git
cd kavachai

# Install dependencies
pip install -r kavachai/backend/requirements.txt

# Run the 5-stage attack demo
python kavachai/backend/demo/run_demo.py
```

You'll see KavachAI catch all 5 attack stages:
```
Stage 1: Indirect Prompt Injection      → 🔴 QUARANTINE (threat: 0.95)
Stage 2: Aadhaar Exfiltration Attempt   → 🔴 QUARANTINE (policy match)
Stage 3: Privilege Escalation           → 🛑 BLOCK (out of scope)
Stage 4: Covert Data Channel            → 🔴 QUARANTINE (policy match)
Stage 5: STAC Sequential Attack Chain   → 🔶 ESCALATE (policy match)
Summary: 5/5 attack stages detected and blocked/escalated
```

### Start the Full System

```bash
# Option 1: Docker (recommended)
docker-compose up
# Backend: http://localhost:8000  |  Dashboard: http://localhost:3000

# Option 2: Manual
# Terminal 1 — Backend
pip install -r kavachai/backend/requirements.txt
uvicorn kavachai.backend.main:app --reload --port 8000

# Terminal 2 — Dashboard
cd kavachai/dashboard && npm install && npm run dev
```

### Verify It's Running

```bash
curl http://localhost:8000/health
# → {"status":"ok","service":"kavachai","version":"0.1.0"}
```

## API Quick Reference

```bash
# Register an agent
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" -H "X-API-Key: demo" \
  -d '{"name":"my-agent","capability_scope":["search","send_email"]}'

# Evaluate an action
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" -H "X-API-Key: demo" \
  -d '{"request_id":"r1","agent_id":"<id>","session_id":"s1","tool_name":"search","parameters":{}}'

# Upload a safety policy
curl -X PUT http://localhost:8000/api/v1/policies \
  -H "Content-Type: application/json" \
  -d '{"name":"my_policy","dsl_source":"policy test\nrule r1 {\n  when tool_call(\"admin_*\")\n  check agent.trust_level != \"trusted\"\n  then block severity high\n}"}'

# View audit trail
curl http://localhost:8000/api/v1/sessions/s1/audit-trail -H "X-API-Key: demo"

# Check compliance
curl http://localhost:8000/api/v1/compliance/dpdp-status
curl http://localhost:8000/api/v1/compliance/seven-sutras

# Manage escalations
curl http://localhost:8000/api/v1/escalations
```


## KavachAI DSL — Policy Language

Write safety rules in a simple, readable format:

```
policy financial_services_safety
version "1.0"

rule block_unauthorized_payment {
  when tool_call("payment_process")
  check action.params.amount > 50000
    and agent.trust_level != "trusted"
  then escalate severity critical
}

rule prevent_aadhaar_exfiltration {
  when tool_call("send_email" | "external_api" | "webhook")
  check data_from "customer_records" reaches "external"
  then quarantine severity critical
}

workflow customer_service {
  state start initial
  state authenticated
  state data_accessed
  state admin_access dangerous

  start -> authenticated on tool_call("verify_identity")
  authenticated -> data_accessed on tool_call("customer_lookup")
  authenticated -> admin_access on tool_call("admin_*")
}
```

## SOC Dashboard

10-page real-time security operations center:

| Page | Purpose |
|------|---------|
| Threat Feed | Live session monitoring, threat scores, alerts |
| Kill Chains | Multi-stage attack visualization with STAC detection |
| Escalations | Human-in-the-loop approve/reject queue |
| Forensics | Step-by-step session replay with 3-layer decision explanations |
| Compliance | DPDP Act status + India AI Seven Sutras radar |
| Agents | Agent registry with trust scores and capability scopes |
| Policies | DSL policy viewer with syntax highlighting |
| Model Eval | LLM safety scores and red team results |
| LLM Usage | Cost tracking, budget utilization, model health |
| Grounding | Semantic grounding reports and claim verification |

## Research Foundation

KavachAI's architecture is grounded in 20 cutting-edge research papers from arXiv and McKinsey. See [specs/requirements.md](specs/requirements.md#research-foundation) for the full research foundation and [specs/knowledge-base.md](specs/knowledge-base.md) for detailed concept explanations.

## Documentation

| Document | Description |
|----------|-------------|
| [docs/TUTORIAL.md](docs/TUTORIAL.md) | Comprehensive getting started tutorial for first-time users |
| [docs/ENTERPRISE-PRODUCTION-PLAN.md](docs/ENTERPRISE-PRODUCTION-PLAN.md) | AWS production deployment plan with Well-Architected Framework |
| [specs/requirements.md](specs/requirements.md) | 31 requirements with user stories, acceptance criteria, and correctness properties |
| [specs/design.md](specs/design.md) | Technical design — architecture, data models, APIs, database schema, DSL grammar |
| [specs/knowledge-base.md](specs/knowledge-base.md) | Educational reference for AI/Agentic AI students covering 15 core concepts |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11+ / FastAPI |
| Frontend | React 18 / Next.js 14 / TailwindCSS |
| Database | SQLite (audit/persistent) + Redis (real-time) |
| DSL Parser | Lark (PEG grammar) |
| Crypto | Ed25519 (PyNaCl) / SHA-256 |
| MCP | mcp Python SDK |
| Deploy | Docker Compose / Railway / Vercel |

## Repository Structure

```
kavachai/
├── kavachai/
│   ├── backend/
│   │   ├── api/                    # REST API routes + WebSocket
│   │   ├── core/                   # Pipeline, policy engine, DSL, identity, trust, DFA
│   │   ├── threat/                 # 5 threat sub-detectors + orchestrator
│   │   ├── audit/                  # Hash chain, evidence packages, session replay
│   │   ├── compliance/             # PII masking, DPDP, Seven Sutras, CERT-In
│   │   ├── ethics/                 # Bias detection, toxicity, ethics engine
│   │   ├── explain/                # Reasoning capture, 3-layer explanations
│   │   ├── grounding/              # Semantic grounding, hallucination detection
│   │   ├── llm/                    # LLM gateway, evaluation, red teaming, observability
│   │   ├── mcp/                    # MCP proxy gateway + safety server
│   │   ├── multi_agent/            # Multi-agent governor, collusion detection
│   │   ├── demo/                   # Demo scenario, sample policies, knowledge graphs
│   │   ├── models/                 # Pydantic data models
│   │   └── db/                     # SQLite + Redis connection managers
│   └── dashboard/                  # Next.js 14 SOC Dashboard (10 pages)
├── specs/                          # Requirements, design, knowledge base
├── docs/                           # Tutorial and documentation
├── Dockerfile.backend              # Backend Docker image
├── docker-compose.yml              # Full stack deployment
├── railway.toml                    # Railway cloud deployment
└── README.md                       # This file
```

## Regulatory Alignment

| Framework | Coverage |
|-----------|---------|
| DPDP Act 2023 (India) | Consent, data localization, PII masking, breach notification |
| India AI Governance 2025 | Seven Sutras compliance mapping and reporting |
| NIST AI RMF 1.0 | Govern, Map, Measure, Manage functions |
| EU AI Act (2024/1689) | Right to explanation, transparency obligations |
| CERT-In | Incident reporting format and evidence packages |

## License

[MIT](LICENSE)

## Acknowledgments

Built for the **ISB Hackathon on Cybersecurity & AI Safety 2025-26**, organized by the Indian School of Business (ISB Mohali), Punjab Police State Cyber Crime Division, and CyberPeace Foundation.

See [References](specs/requirements.md#references-and-acknowledgments) for full source citations.
