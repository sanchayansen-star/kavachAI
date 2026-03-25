# KavachAI (कवच) — Zero Trust Safety Firewall for Agentic AI

> A production-grade governance platform for autonomous AI agents, built for the ISB Hackathon on Cybersecurity & AI Safety 2025-26.

**Kavach** (कवच) means "armor" or "protective shield" in Sanskrit — reflecting the system's role as a protective governance layer for autonomous AI agents.

---

## What is KavachAI?

KavachAI is a Zero Trust safety firewall that sits between AI agents and their tools, enforcing safety policies, detecting threats, ensuring regulatory compliance, and providing tamper-proof audit trails — all in real time.

It operates as an **MCP Proxy Gateway**, transparently intercepting all tool calls between any MCP-compatible agent (Claude, GPT, LangChain, CrewAI) and any MCP server (tools), running a 10-stage evaluation pipeline before allowing actions to execute.

## Key Capabilities

| Capability | Description |
|-----------|-------------|
| Zero Trust Identity | Ed25519 cryptographic agent identities with scoped capability tokens |
| KavachAI DSL | Formal policy language with LTL temporal logic and DFA behavioral modeling |
| Threat Detection | Prompt injection, STAC attacks, privilege escalation, covert channels, kill chain analysis |
| MCP Proxy Gateway | Protocol-native governance for any MCP-compatible agent and tool |
| Multi-LLM Gateway | Unified routing to OpenAI, Anthropic, Google, open-source models with safety governance |
| Semantic Grounding | Deterministic validation against knowledge graphs and domain ontologies |
| AI Ethics Engine | Bias detection (India-specific), toxicity filtering, fairness monitoring |
| DPDP Act Compliance | Aadhaar/PAN masking, consent verification, data localization, breach notification |
| Seven Sutras Compliance | Full mapping to India's AI Governance Guidelines 2025 |
| Cryptographic Audit Trail | SHA-256 hash chains, evidence packages, CERT-In reporting |
| SOC Dashboard | Real-time threat visualization, kill chain analysis, forensic investigation |
| LLM Evaluation | Automated safety benchmarking and red-teaming before model deployment |
| LLM Explainability | 3-layer decision explanations (LLM reasoning, policy, user-facing) |
| Semantic Grounding Layer | Deterministic fact-checking against knowledge graphs (no LLM dependency) |

## Research Foundation

KavachAI's architecture is grounded in 20 cutting-edge research papers from arXiv and McKinsey. See [specs/requirements.md](specs/requirements.md#research-foundation) for the full research foundation and [specs/knowledge-base.md](specs/knowledge-base.md) for detailed concept explanations.

## Project Documentation

| Document | Description |
|----------|-------------|
| [specs/requirements.md](specs/requirements.md) | 31 requirements with user stories, acceptance criteria, and correctness properties |
| [specs/design.md](specs/design.md) | Technical design — architecture, data models, APIs, database schema, DSL grammar |
| [specs/knowledge-base.md](specs/knowledge-base.md) | Educational reference for AI/Agentic AI students covering 15 core concepts |

## Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Backend | Python 3.11+ / FastAPI | Async-native, auto-generated OpenAPI docs, rich AI/ML ecosystem |
| Frontend | React 18 / Next.js / TailwindCSS | SSR performance, rich component ecosystem, Vercel-native |
| Database | SQLite | Zero-config, single-file, hash chain integrity |
| Cache | Redis | Pub/sub for real-time dashboard, rate limiting, session state |
| DSL Parser | PEG (lark) | Composable grammars, excellent error messages |
| Crypto | Ed25519 (PyNaCl) / SHA-256 | Fast signing, compact keys, industry-standard hashing |
| MCP | mcp Python SDK | Official SDK for proxy gateway and safety server |
| LLM | LiteLLM / provider SDKs | Unified interface to 100+ LLM providers |
| Deploy | Railway + Vercel + Docker | Cloud hosting with local fallback |

## Deployment Model

KavachAI uses a **hybrid cloud + local** deployment:
- **Cloud**: Railway (backend + Redis) + Vercel (dashboard) — public HTTPS URLs for external access
- **Local**: Docker Compose — single `docker-compose up` for offline/demo environments
- **Data Sovereignty**: All data stored locally on deployment host, aligned with DPDP Act

## Quick Start

```bash
# Clone
git clone https://gitlab.com/sanchayan1/kavachai.git
cd kavachai

# Run with Docker (when implementation is ready)
docker-compose up

# Access points
# SOC Dashboard: http://localhost:3000
# REST API:      http://localhost:8000
# MCP Proxy:     localhost:3001
```

## Repository Structure

```
kavachai/
├── specs/                          # Project specifications
│   ├── requirements.md             # 31 requirements with acceptance criteria
│   ├── design.md                   # Technical design document
│   └── knowledge-base.md           # Core concepts knowledge base
├── docs/                           # Documentation index
│   └── README.md                   # Documentation guide
├── backend/                        # Python FastAPI backend (implementation phase)
├── dashboard/                      # React SOC dashboard (implementation phase)
├── .kiro/                          # Kiro IDE spec files (internal)
├── README.md                       # This file
├── LICENSE                         # MIT License
├── CONTRIBUTING.md                 # Contribution guidelines
├── CHANGELOG.md                    # Version history
└── .gitignore                      # Git ignore rules
```

## Regulatory Alignment

| Framework | Coverage |
|-----------|---------|
| DPDP Act 2023 (India) | Consent, data localization, PII masking, breach notification, right to erasure |
| India AI Governance Guidelines 2025 | Seven Sutras compliance mapping and reporting |
| NIST AI RMF 1.0 | Govern, Map, Measure, Manage functions |
| EU AI Act (2024/1689) | Right to explanation, transparency obligations |
| CERT-In | Incident reporting format and webhook integration |

## License

[MIT](LICENSE)

## Acknowledgments

Built for the **ISB Hackathon on Cybersecurity & AI Safety 2025-26**, organized by the Indian School of Business (ISB Mohali), Punjab Police State Cyber Crime Division, and CyberPeace Foundation.

See [References](specs/requirements.md#references-and-acknowledgments) for full source citations.
