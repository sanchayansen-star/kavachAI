# KavachAI (कवच) — Zero Trust Safety Firewall for Agentic AI

> A production-grade governance platform for autonomous AI agents, built for the ISB Hackathon on Cybersecurity & AI Safety 2025-26.

KavachAI is a Zero Trust safety firewall that sits between AI agents and their tools, enforcing safety policies, detecting threats, ensuring regulatory compliance, and providing tamper-proof audit trails — all in real time.

## Key Capabilities

- **Zero Trust Agent Identity** — Ed25519 cryptographic identities with scoped capability tokens
- **KavachAI DSL** — Formal policy language with temporal logic (LTL) and DFA behavioral modeling
- **Advanced Threat Detection** — Prompt injection, STAC attacks, privilege escalation, covert channels
- **MCP Proxy Gateway** — Protocol-native governance for any MCP-compatible agent and tool
- **Multi-LLM Gateway** — Unified routing to OpenAI, Anthropic, Google, and open-source models
- **Semantic Grounding Layer** — Deterministic validation against knowledge graphs and domain ontologies
- **AI Ethics Engine** — Bias detection (India-specific), toxicity filtering, fairness monitoring
- **DPDP Act 2023 Compliance** — Aadhaar/PAN masking, consent verification, data localization
- **India AI Governance (Seven Sutras)** — Full compliance mapping and reporting
- **Cryptographic Audit Trail** — SHA-256 hash chains, evidence packages, CERT-In reporting
- **SOC Dashboard** — Real-time threat visualization, kill chain analysis, forensic investigation
- **LLM Evaluation** — Automated safety benchmarking and red-teaming before model deployment

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11+ / FastAPI |
| Frontend | React 18 / Next.js / TailwindCSS |
| Database | SQLite (hash chain audit) |
| Cache | Redis (real-time state) |
| DSL Parser | PEG (lark) |
| Crypto | Ed25519 (PyNaCl) / SHA-256 |
| MCP | mcp Python SDK |
| LLM | LiteLLM / provider SDKs |
| Deploy | Railway + Vercel + Docker |

## Quick Start

```bash
# Clone and run with Docker
docker-compose up

# Access
# SOC Dashboard: http://localhost:3000
# REST API: http://localhost:8000
# MCP Proxy: localhost:3001
```

## Project Structure

See `.kiro/specs/agent-shield-safety-firewall/` for full spec documentation:
- `requirements.md` — 31 requirements with acceptance criteria
- `design.md` — Technical design with architecture, data models, APIs
- `knowledge-base.md` — Educational reference for AI/Agentic AI concepts

## Research Foundation

Built on 20 research papers from arXiv and McKinsey. See the References section in `requirements.md` for full citations.

## License

MIT

## Acknowledgments

Kavach (कवच) means "armor" in Sanskrit. Built for the ISB Hackathon on Cybersecurity & AI Safety 2025-26, organized by ISB Mohali, Punjab Police, and CyberPeace Foundation.
