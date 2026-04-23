# KavachAI — Executive Business Case

> Zero Trust Safety Firewall for Agentic AI

---

## The 30-Second Pitch

Your company is deploying AI agents that can take real actions — process payments, access
customer data, call APIs. KavachAI is the security firewall that sits between those agents
and your systems. Every action an agent tries to take passes through our 10-stage safety
check in under 100 milliseconds. We catch prompt injection attacks, data exfiltration,
privilege escalation, and policy violations before they happen — not after. Think of it as
a network firewall, but purpose-built for AI agents, with built-in multi-jurisdiction
compliance for DPDP Act (India), GDPR (EU), FCA/PRA (UK), and international AI governance
frameworks.

---

## The Problem

Enterprises are racing to deploy AI agents — autonomous systems that can take actions on
behalf of users. But these agents introduce a new attack surface that traditional security
tools were never designed for.

| Threat | What Happens | Traditional Tools Detect It? |
|--------|-------------|------------------------------|
| Prompt injection | Attacker hides instructions in customer data that hijack the agent | No |
| Data exfiltration | Agent is tricked into emailing Aadhaar numbers to an external address | No |
| Privilege escalation | Agent gradually expands its own access through a sequence of calls | No |
| Sequential attack chains | Each individual action looks harmless, but the sequence is an attack | No |
| Hallucination | Agent fabricates tool results or misrepresents data to users | No |
| Covert channels | Sensitive data encoded in base64 or steganography within normal outputs | No |

Today, most organizations have **zero visibility** into what their AI agents are actually
doing. There is no audit trail, no policy enforcement, and no real-time threat detection at
the agent decision layer.

### The Regulatory Reality

- **DPDP Act 2023** penalties up to ₹250 crore for data protection violations
- **India AI Governance Guidelines 2025** require accountability, transparency, and fairness
- **CERT-In** mandates incident reporting within 6 hours of detection
- **GDPR** fines up to €20 million or 4% of global annual turnover (whichever is higher)
- **EU AI Act** requires right-to-explanation for automated decisions, conformity assessments for high-risk AI
- **FCA (UK)** Consumer Duty fines with no upper cap — recent fines have exceeded £100 million
- **PRA SS1/23** requires model risk management for all AI/ML models used in UK financial services
- **DORA** mandates ICT risk management and incident reporting for EU financial entities

An AI agent that processes customer data without proper governance exposes the enterprise to
all of these simultaneously — across every jurisdiction it operates in.

---

## The Solution: KavachAI

KavachAI is a Zero Trust governance layer for AI agents. It intercepts every tool call an
agent makes and runs it through a 10-stage evaluation pipeline:

```
AI Agent Action → KavachAI Pipeline → Tool Execution (or Block)

Pipeline stages:
1. Identity Verification    — Is this a known, authenticated agent?
2. Capability Token Check   — Does it have permission for this specific tool?
3. Policy Enforcement       — Do the safety rules allow this action?
4. Threat Detection         — Is this a prompt injection, escalation, or attack?
5. DPDP Compliance          — Does this comply with data protection law?
6. Ethics Screening         — Is this biased, toxic, or unfair?
7. PII Masking              — Are Aadhaar, PAN, mobile numbers protected?
8. Reasoning Capture        — Record the agent's decision rationale for audit
9. Semantic Grounding       — Are the agent's claims factually accurate?
10. Cryptographic Attestation — Sign and seal the verdict in the audit trail
```

All 10 stages execute in under 100 milliseconds. If any stage detects a problem, the
pipeline short-circuits immediately — the dangerous action never reaches your systems.

---

## Business Value

### 1. Risk Reduction

In our demonstration scenario, KavachAI catches **5 out of 5 sophisticated attack stages**
against a financial services AI agent:

| Attack | KavachAI Response |
|--------|------------------|
| Prompt injection hidden in customer message | QUARANTINE (threat score: 0.95) |
| Aadhaar exfiltration via email | QUARANTINE (policy: data flow to external) |
| Privilege escalation to admin tools | BLOCK (not in capability scope) |
| Covert data channel via base64 encoding | QUARANTINE (policy: exfiltration pattern) |
| Sequential tool attack chain (STAC) | ESCALATE (policy: unauthorized payment) |

These are attacks that no traditional SIEM, EDR, or WAF would detect because they operate
at the semantic layer of AI agent behavior, not at the network or endpoint layer.

### 2. Regulatory Compliance

KavachAI is a **jurisdiction-aware** compliance platform. Tenants configure which jurisdictions apply, and all relevant compliance engines run in parallel.

| Regulation | Jurisdiction | KavachAI Coverage |
|-----------|-------------|-------------------|
| DPDP Act 2023 | India | Real-time PII masking (Aadhaar, PAN, mobile, UPI), consent verification, data localization enforcement, breach notification triggers |
| India AI Seven Sutras | India | Quantified compliance scores across all 7 principles (Trust, People First, Innovation, Fairness, Accountability, Understandable, Safety) |
| CERT-In | India | Automated incident report generation in CERT-In format with cryptographically signed evidence packages |
| GDPR | EU | Lawful basis tracking, right to erasure, data portability, 72-hour breach notification, DPIA status, cross-border transfer controls (SCCs, BCRs, adequacy decisions) |
| EU AI Act (2024/1689) | EU | Risk classification, 3-layer decision explanations (right to explanation), transparency obligations, conformity assessment support for high-risk AI |
| DORA | EU | ICT risk management status, incident reporting, third-party risk management for financial entities |
| MiFID II | EU | Algorithmic trading controls, best execution, transaction reporting |
| PSD2 | EU | Strong customer authentication tracking, open banking security |
| EBA Guidelines on AI/ML | EU | Model risk management, explainability for credit decisions |
| UK GDPR + DPA 2018 | UK | Post-Brexit UK data protection (mirrors EU GDPR with UK-specific provisions) |
| FCA Consumer Duty | UK | Treating customers fairly, good outcomes, operational resilience |
| PRA SS1/23 | UK | Model risk management, capital adequacy, stress testing |
| SM&CR | UK | Individual accountability mapping — which senior manager is responsible for each AI system |
| UK AI Regulation | UK | Principles-based compliance: safety, transparency, fairness, accountability, contestability |
| NIST AI RMF 1.0 | International | Govern, Map, Measure, Manage functions |

This is not a periodic audit — it is continuous, real-time compliance enforcement on every
agent action.

### 3. Audit and Accountability

Every agent action is recorded in a **tamper-proof cryptographic audit trail**:

- SHA-256 hash chains link every entry to the previous one (like a blockchain)
- Monotonic sequence numbers detect any deletion attempts
- Evidence packages can be exported with digital signatures for legal proceedings
- Session replay allows step-by-step forensic investigation of any incident

You can prove to any regulator, auditor, or court exactly what every agent did, when it did
it, and why it was allowed or blocked.

### 4. Operational Control

A real-time **SOC Dashboard** (10 pages) gives your security team:

- Live threat feed with session-level threat scores
- Kill chain visualization showing multi-stage attack progression
- Escalation queue where human operators approve or reject high-risk actions
- Forensic investigation with 3-layer decision explanations
- Compliance posture with DPDP and Seven Sutras scoring
- Agent registry with dynamic trust scores
- LLM model safety evaluation and cost tracking

### 5. Vendor Independence

KavachAI works with **any AI agent framework** (Claude, GPT, LangChain, CrewAI, AutoGen,
custom agents) and **any tool provider** through the Model Context Protocol (MCP) standard.
No vendor lock-in. No agent code changes required.

---

## Financial Analysis

### Cost of Inaction

| Risk | Jurisdiction | Potential Cost |
|------|-------------|---------------|
| DPDP Act violation (single incident) | India | Up to ₹250 crore |
| GDPR violation (single incident) | EU | Up to €20 million or 4% of global annual turnover |
| FCA fine (Consumer Duty breach) | UK | No upper cap — recent fines have exceeded £100 million |
| PRA enforcement action | UK | Unlimited — includes potential restriction of business activities |
| Data breach (average, India) | India | ₹17.9 crore (IBM Cost of Data Breach 2024) |
| Data breach (average, EU) | EU | €4.35 million (IBM Cost of Data Breach 2024) |
| Reputation damage | Global | Unquantifiable but significant |
| Regulatory investigation | Multi | ₹1-5 crore / €500K-2M in legal and compliance costs per jurisdiction |
| Customer churn from trust erosion | Global | 5-15% revenue impact |

### Cost of KavachAI

| Deployment Tier | Evaluations/Day | Monthly Cost | Cost per Evaluation |
|----------------|-----------------|-------------|---------------------|
| Starter | 10,000 | ~$500 (₹42,000) | $0.0017 |
| Growth | 100,000 | ~$800 (₹67,000) | $0.00027 |
| Enterprise | 1,000,000 | ~$2,500 (₹2,10,000) | $0.000083 |
| Scale | 10,000,000 | ~$8,000 (₹6,70,000) | $0.000027 |

For context: the Growth tier costs less than one security analyst's monthly salary while
providing 24/7 real-time evaluation of every agent action.

### ROI Calculation

**Conservative scenario:** KavachAI prevents one moderate data incident per year.

- Cost of incident avoided: ₹5 crore (regulatory fine + remediation + legal)
- Annual KavachAI cost (Growth tier): ₹8 lakh
- **ROI: 62x return on investment**

**Realistic scenario:** KavachAI prevents multiple incidents and reduces compliance audit costs.

- Incidents avoided: ₹5-20 crore
- Compliance audit cost reduction: ₹50 lakh (automated evidence, continuous monitoring)
- Annual KavachAI cost: ₹8-25 lakh
- **ROI: 30-100x return on investment**

---

## Competitive Differentiation

| Capability | KavachAI | Traditional SIEM/EDR | Generic AI Guardrails |
|-----------|----------|---------------------|----------------------|
| Agent-level threat detection | ✅ Purpose-built | ❌ Network/endpoint only | ⚠️ Basic prompt filtering |
| Formal policy language (DSL) | ✅ With temporal logic and DFA | ❌ | ❌ |
| Cryptographic audit trail | ✅ SHA-256 hash chains | ⚠️ Log-based (mutable) | ❌ |
| Multi-jurisdiction compliance | ✅ India + EU + UK (jurisdiction-aware) | ❌ | ❌ |
| DPDP Act compliance | ✅ Real-time enforcement | ❌ | ❌ |
| GDPR compliance | ✅ Lawful basis, erasure, portability, breach notification | ❌ | ❌ |
| UK FCA/PRA compliance | ✅ Consumer Duty, SS1/23, SM&CR | ❌ | ❌ |
| India AI Seven Sutras | ✅ Quantified scoring | ❌ | ❌ |
| EU AI Act conformity | ✅ Risk classification, right to explanation | ❌ | ⚠️ Basic |
| MCP protocol native | ✅ Transparent proxy | ❌ | ❌ |
| Kill chain analysis for agents | ✅ STAC detection | ⚠️ Network kill chains only | ❌ |
| Multi-agent governance | ✅ Delegation limits, collusion detection | ❌ | ❌ |
| Semantic grounding | ✅ Knowledge graph verification | ❌ | ❌ |
| Sub-100ms latency | ✅ | N/A | ⚠️ Varies |

---

## Deployment Timeline

| Phase | Duration | Milestone |
|-------|----------|-----------|
| Foundation | Weeks 1-2 | Infrastructure on AWS, CI/CD pipeline, security review |
| Internal Pilot | Weeks 3-4 | 1-2 internal agents protected, SOC team trained |
| Limited Production | Weeks 5-8 | First business unit live, escalation workflows operational |
| Enterprise Rollout | Weeks 9-16 | All agents protected, DR tested, full compliance active |

**Time to first value: 2 weeks** (internal pilot with real threat detection).

---

## Technology Overview (for CTO/CIO)

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | Python / FastAPI | Async-native, sub-100ms pipeline, rich AI/ML ecosystem |
| Dashboard | React / Next.js | Real-time SOC operations, 10 specialized pages |
| Database | Aurora PostgreSQL (production) | Multi-AZ, tamper-proof audit trail, point-in-time recovery |
| Cache | ElastiCache Redis | Real-time session state, pub/sub for dashboard, rate limiting |
| Crypto | Ed25519 / SHA-256 | Industry-standard signing and hashing, hardware-backed via KMS |
| Protocol | MCP (Model Context Protocol) | Industry standard for agent-tool communication |
| Infrastructure | AWS (ECS Fargate, Aurora, S3) | Serverless compute, multi-region deployment (India: Mumbai, EU: Ireland, UK: London) |

Full AWS architecture with Well-Architected Framework compliance is documented in
[ENTERPRISE-PRODUCTION-PLAN.md](ENTERPRISE-PRODUCTION-PLAN.md).

---

## Addressing Executive Concerns

### "How does this integrate with our existing stack?"

KavachAI operates as a transparent proxy. Your agents don't need code changes. You point
them at KavachAI's proxy instead of directly at tools, and every call is intercepted,
evaluated, and forwarded or blocked. Same pattern as a web application firewall, but for
AI agent tool calls.

### "What if KavachAI itself goes down?"

Multi-AZ deployment with automatic failover. RTO under 15 minutes, RPO under 1 minute.
If the evaluation pipeline is unreachable, the configurable safe default is BLOCK — no
agent action proceeds without governance. This is the Zero Trust principle: deny by default.

### "Does this slow down our agents?"

The full 10-stage pipeline executes in under 100 milliseconds (p95). For comparison, a
typical LLM API call takes 1-3 seconds. KavachAI adds less than 5% overhead to the total
agent action time.

### "Can we customize the safety rules?"

Yes. KavachAI includes a purpose-built policy language (DSL) that security teams can write
and update without code deployments. Policies support temporal logic ("block if X happens
within 5 minutes of Y"), behavioral state machines ("agent must follow this workflow"),
and India-specific constructs ("ensure fairness in loan processing for all demographic
groups"). Policies hot-reload in under 5 seconds.

### "Who else is using this?"

KavachAI was built for the ISB Hackathon on Cybersecurity & AI Safety 2025-26, organized
by the Indian School of Business, Punjab Police Cyber Crime Division, and CyberPeace
Foundation. It is designed for enterprises deploying AI agents in regulated industries —
financial services, healthcare, government, and telecommunications.

---

## Next Steps

1. **30-minute demo:** See KavachAI catch a live 5-stage attack against a financial services agent
2. **2-week pilot:** Deploy KavachAI with 1-2 internal agents, measure threat detection accuracy
3. **Production proposal:** Detailed architecture review, cost estimate, and rollout plan for your environment

---

*KavachAI (कवच) — "Armor" for your AI agents.*
