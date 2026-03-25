# Requirements Document — KavachAI: Zero Trust Safety Firewall for Agentic AI

## Table of Contents

- [Introduction](#introduction)
- [Research Foundation](#research-foundation)
- [Glossary](#glossary)
- [Requirements](#requirements)
  - [1. Zero Trust Agent Identity and Authentication](#requirement-1-zero-trust-agent-identity-and-authentication)
  - [2. KavachAI DSL — Formal Policy Language](#requirement-2-kavachai-dsl--formal-policy-language)
  - [3. Advanced Threat Detection Engine](#requirement-3-advanced-threat-detection-engine)
  - [4. DPDP Act 2023 Compliance Engine](#requirement-4-dpdp-act-2023-compliance-engine)
  - [5. Action Interception and Zero Trust Evaluation Pipeline](#requirement-5-action-interception-and-zero-trust-evaluation-pipeline)
  - [6. Cryptographic Audit Trail and Evidence Chain](#requirement-6-cryptographic-audit-trail-and-evidence-chain)
  - [7. Multi-Agent Governance](#requirement-7-multi-agent-governance)
  - [8. Human-in-the-Loop Escalation with Forensic Context](#requirement-8-human-in-the-loop-escalation-with-forensic-context)
  - [9. SOC-Style Real-Time Threat Intelligence Dashboard](#requirement-9-soc-style-real-time-threat-intelligence-dashboard)
  - [10. Law Enforcement Integration and Incident Reporting](#requirement-10-law-enforcement-integration-and-incident-reporting)
  - [11. Framework-Agnostic SDK and REST API](#requirement-11-framework-agnostic-sdk-and-rest-api)
  - [12. FastAPI Backend Infrastructure](#requirement-12-fastapi-backend-infrastructure)
  - [13. Demo Scenario — Multi-Stage Financial Services Attack](#requirement-13-demo-scenario--multi-stage-financial-services-attack)
  - [14. Formal Policy Verification (Dual-Stage)](#requirement-14-formal-policy-verification-dual-stage)
  - [15. DFA-Based Behavioral Modeling](#requirement-15-dfa-based-behavioral-modeling)
  - [16. Dynamic Trust Scoring](#requirement-16-dynamic-trust-scoring)
  - [17. Determinism Assurance for Regulatory Audit](#requirement-17-determinism-assurance-for-regulatory-audit)
  - [18. MCP Proxy Gateway Architecture](#requirement-18-mcp-proxy-gateway-architecture)
  - [19. MCP Safety Server](#requirement-19-mcp-safety-server)
  - [20. Deployment and Hosting Infrastructure](#requirement-20-deployment-and-hosting-infrastructure)
  - [21. Multi-LLM Gateway and LLM-as-a-Service](#requirement-21-multi-llm-gateway-and-llm-as-a-service)
  - [22. AI Ethics and Responsible AI Guardrails](#requirement-22-ai-ethics-and-responsible-ai-guardrails)
  - [23. Hallucination Detection and Output Grounding](#requirement-23-hallucination-detection-and-output-grounding)
  - [24. India AI Governance Guidelines Compliance](#requirement-24-india-ai-governance-guidelines-compliance)
  - [25. LLM Cost and Usage Governance](#requirement-25-llm-cost-and-usage-governance)
  - [26. LLM Explainability and Decision Transparency](#requirement-26-llm-explainability-and-decision-transparency)
  - [27. Model Transparency and Provenance](#requirement-27-model-transparency-and-provenance)
  - [28. LLM Observability and Performance Monitoring](#requirement-28-llm-observability-and-performance-monitoring)
  - [29. Multi-Tenant Enterprise Deployment](#requirement-29-multi-tenant-enterprise-deployment)
  - [30. LLM Evaluation and Continuous Safety Benchmarking](#requirement-30-llm-evaluation-and-continuous-safety-benchmarking)
  - [31. Semantic Grounding Layer](#requirement-31-semantic-grounding-layer)
- [Technology Stack Rationale and Deployment Model](#technology-stack-rationale-and-deployment-model)
- [References and Acknowledgments](#references-and-acknowledgments)

---

## Introduction

KavachAI is a production-grade, Zero Trust safety firewall for autonomous AI agent systems — designed as critical national security infrastructure for governing agentic AI in India. Built for the ISB Hackathon on Cybersecurity & AI Safety 2025-26 (Agentic AI Safety track, organized by ISB Mohali with Punjab Police and CyberPeace Foundation), KavachAI addresses a fundamental gap in the current AI ecosystem: the absence of a comprehensive, enforceable, and auditable governance layer for AI agents that autonomously invoke tools, access data, and make decisions.

As McKinsey's 2025 research confirms, 80% of organizations have already encountered risky behavior from AI agents — including improper data exposure and unauthorized system access. AI agents are effectively "digital insiders": entities operating within systems with varying privilege levels, capable of chaining vulnerabilities across trust boundaries. As Rich Isenberg (McKinsey Partner) states: "Agency isn't a feature — it's a transfer of decision rights." And critically: "The scariest failures are the ones you can't reconstruct, because you didn't log the workflow." KavachAI is built to ensure every workflow is fully reconstructable, every decision is auditable, and every agent action is governed.

Unlike simple policy-based filters, KavachAI implements a full Zero Trust Architecture where no agent action is implicitly trusted. Every tool call is continuously authenticated, authorized against scoped credentials, evaluated against formal safety policies expressed in a purpose-built Domain-Specific Language (KavachAI DSL), and cryptographically attested in a tamper-proof audit chain. The system defends against sophisticated multi-stage attacks including indirect prompt injection, tool poisoning, privilege escalation, covert data exfiltration, and multi-agent collusion — threat vectors that are actively exploited in real-world agentic deployments.

KavachAI directly implements McKinsey's recommended three-phase approach to agentic AI safety: (1) risk assessment through formal policy verification and DFA-based behavioral modeling, (2) least-privilege controls through Zero Trust identity management and scoped capability tokens, and (3) anomaly monitoring through advanced threat detection, dynamic trust scoring, and real-time SOC dashboard visualization.

KavachAI represents a practical implementation of the fusion of LLMs and formal methods — using formal verification techniques (Deterministic Finite Automata, Linear Temporal Logic, hash chains, dual-stage verification) to govern LLM agent behavior, while keeping the system accessible through a human-readable DSL that does not require deep formal methods expertise from users. The system is designed to be generally accessible: security policy authors write policies in plain-English-like DSL syntax, the SOC dashboard provides intuitive visualizations, and the SDK integrates with a few lines of code.

KavachAI is built with India's regulatory landscape at its core. A native DPDP Act 2023 compliance engine enforces data localization, consent verification, Aadhaar/PAN masking, and automated breach notification — making it immediately deployable in Indian financial services, healthcare, and government contexts. The cryptographic audit trail produces evidence-grade logs suitable for law enforcement investigation, CERT-In reporting, and judicial proceedings — directly relevant to Punjab Police's cybercrime division and India's evolving AI governance framework.

The system governs not just individual agents but multi-agent ecosystems — monitoring inter-agent communication, tracking delegation chains, analyzing collective behavior, and preventing agent collusion. A real-time Security Operations Center (SOC) dashboard provides live threat scoring, attack kill chain visualization, compliance posture monitoring, and forensic investigation capabilities.

KavachAI is framework-agnostic, providing a protocol-level integration layer (Python SDK + REST API) compatible with LangChain, CrewAI, AutoGen, and custom agent frameworks. The tech stack is deliberately practical: Python/FastAPI backend, React dashboard, SQLite with hash-chain integrity for audit, Redis for real-time state, and a PEG-based parser for the KavachAI DSL.

KavachAI also functions as an LLM-as-a-Service gateway, providing a unified interface for routing agent LLM requests to multiple model providers (OpenAI, Anthropic, Google, open-source models) with consistent safety governance, cost tracking, and intelligent fallback routing. The system enforces comprehensive AI ethics guardrails — bias detection (with India-specific categories including caste, gender, religion, and regional bias), toxicity filtering, hallucination detection (including tool-call fabrication), fairness monitoring, and content safety classification. These ethical guardrails are mapped to India's AI Governance Guidelines 2025 ('Seven Sutras': Trust, People First, Innovation over Restraint, Fairness & Equity, Accountability, Understandable by Design, Safety/Resilience/Sustainability) and the NIST AI Risk Management Framework, ensuring alignment with both national and international responsible AI standards.

Every agent decision is explainable at multiple levels — the LLM's own chain-of-thought reasoning, the policy evaluation rationale, and a plain-language summary suitable for affected individuals — ensuring compliance with right-to-explanation requirements under DPDP Act and EU AI Act. Full model transparency is maintained through model cards, provenance records, and real-time LLM observability, enabling regulatory auditors to assess model appropriateness and detect performance drift.

**Demo Scenario:** A financial services AI agent handling customer queries is targeted by a sophisticated multi-stage attack — indirect prompt injection via a crafted customer message, attempted exfiltration of Aadhaar numbers through seemingly innocent API responses, privilege escalation to admin-level tool access, and covert data channeling via steganographic encoding in output payloads. KavachAI detects and neutralizes each attack stage, with the SOC dashboard rendering the full kill chain in real time.

[↑ Back to Top](#table-of-contents)

## Research Foundation

KavachAI's architecture is grounded in cutting-edge research from the AI safety, formal methods, and enterprise governance communities. The following works directly inform the system's design and requirements:

1. **AgentSpec — Customizable Runtime Enforcement DSL** (arXiv:2503.18666): A lightweight domain-specific language for specifying and enforcing runtime constraints on LLM agents using trigger-predicate-enforcement patterns. Achieves 90%+ unsafe execution prevention with millisecond-level overhead. KavachAI's DSL adopts this trigger-predicate-enforcement pattern as its core policy evaluation model.

2. **VeriGuard — Dual-Stage Formal Verification** (arXiv:2510.05156): Provides formal safety guarantees through offline verification (intent clarification → behavioral policy synthesis → formal proof of compliance) combined with online runtime monitoring (lightweight action validation against pre-verified policies). KavachAI implements this dual-stage approach for policy verification.

3. **Temporal Logic for Agent Correctness** (arXiv:2509.20364): Applies temporal expression language from hardware verification to monitor AI agent behavior, focusing on execution traces of tool calls and state transitions rather than text matching. Temporal assertions capture correct behavioral patterns across execution scenarios. KavachAI's DSL supports Linear Temporal Logic (LTL) operators inspired by this work.

4. **CORE Framework — DFA-Based Agent Evaluation** (arXiv:2509.20998): Uses Deterministic Finite Automata (DFAs) to encode tasks as sets of valid tool-use paths, enabling principled assessment of agent behavior with metrics including Path Correctness, Prefix Criticality, Harmful-Call Rate, and Efficiency. KavachAI uses DFA-based behavioral modeling for runtime path validation.

5. **DFAH — Determinism-Faithfulness Assurance Harness** (arXiv:2601.15322): Measures trajectory determinism, decision determinism, and evidence-conditioned faithfulness. Key finding: decision determinism and task accuracy are NOT correlated — both must be measured independently. KavachAI incorporates determinism measurement into its audit trail for regulatory compliance.

6. **ShieldAgent — Verifiable Safety Policy Reasoning** (arXiv:2503.22738): First guardrail agent that enforces safety policy compliance through logical reasoning by constructing probabilistic rule circuits from policy documents. Outperforms prior methods by 11.3% while reducing API queries by 64.7% and inference time by 58.2%. KavachAI's Policy Engine adopts probabilistic rule circuits for efficient policy evaluation.

7. **STAC — Sequential Tool Attack Chaining** (arXiv:2509.25624): Demonstrates that chaining individually harmless tool calls can enable harmful operations with attack success rates exceeding 90% against SOTA agents. Existing prompt-based defenses provide limited protection; reasoning-driven defense (evaluating cumulative effects) cuts attack success rate by up to 28.8%. KavachAI's Attack_Chain_Analyzer explicitly defends against STAC-style attacks.

8. **Governance-as-a-Service** (arXiv:2508.18765): A modular, policy-driven enforcement layer that governs agent outputs at runtime without altering model internals. Introduces a Trust Factor mechanism that scores agents based on compliance history and severity-weighted violations, supporting graduated enforcement and dynamic trust modulation. KavachAI implements dynamic trust scoring inspired by this work.

9. **Fusion of LLMs and Formal Methods** (arXiv:2412.06512): A roadmap for integrating LLM flexibility with formal methods rigor — formal methods help LLMs generate certified outputs, while LLMs enhance usability and scalability of formal method tools. KavachAI is positioned as a practical implementation of this fusion.

10. **McKinsey — "Deploying Agentic AI with Safety and Security"** (October 2025): Reports that 80% of organizations have encountered risky behavior from AI agents. Identifies agents as "digital insiders" and highlights chained vulnerabilities and cross-agent task escalation as key risk drivers. Recommends a three-phase approach: risk assessment → least-privilege controls → anomaly monitoring. KavachAI's architecture directly implements this three-phase shield.

11. **McKinsey — "Trust in the Age of Agents"** (March 2026): Frames agency as "a transfer of decision rights" and emphasizes that the scariest failures are those that cannot be reconstructed due to insufficient logging. Reports 80% of organizations encountering risky agent behavior including improper data exposure and unauthorized system access. Validates KavachAI's cryptographic audit trail and full workflow reconstructability.

12. **Capability-Enhanced MCP Framework for Verifiable Safety** (arXiv:2601.08012): Proposes applying System-Theoretic Process Analysis (STPA) to identify hazards in agent workflows and formalizing them as enforceable specifications. Introduces a capability-enhanced Model Context Protocol (MCP) framework with structured labels on capabilities, confidentiality, and trust level. KavachAI implements this as an MCP proxy gateway.

13. **MCPShield — Security Cognition Layer for MCP Agents** (arXiv:2602.14281): A lifecycle-wide security layer between agents and untrusted MCP servers. Verifies consistency between server declared capabilities and actual services during pre-invocation, monitors runtime behaviors during execution, and evaluates long-term behavioral consistency post-invocation. KavachAI's MCP proxy implements this three-phase lifecycle security.

14. **Tool Receipts for Hallucination Detection** (arXiv:2603.10060): AI agents frequently hallucinate results — fabricating tool executions, misstating output counts, or presenting inferences as verified facts. Proposes "tool receipts" as lightweight cryptographic proofs that a tool was actually executed. KavachAI's Action_Attestation mechanism serves as tool receipts, and the system adds hallucination detection for tool-call fabrication.

15. **Comprehensive LLM Guardrails Taxonomy** (arXiv:2406.12934): Proposes a four-dimensional taxonomy for LLM guardrails: trustworthiness, ethics & bias, safety, and legal compliance. Emphasizes intrinsic and extrinsic bias evaluation, fairness metrics, and the need for testability and fail-safes in agentic LLMs. KavachAI implements all four dimensions.

16. **India AI Governance Guidelines** (MeitY, November 2025): India's national framework for responsible AI built on seven principles ("Seven Sutras"): Trust, People First, Innovation over Restraint, Fairness & Equity, Accountability, Understandable by Design, and Safety/Resilience/Sustainability. KavachAI maps its capabilities to each of these seven principles.

17. **Explainability in Agentic AI Systems** (arXiv:2601.17168): Argues that current interpretability techniques developed for static models show limitations when applied to agentic systems. Temporal dynamics, compounding decisions, and context-dependent behaviors demand new analytical approaches. Proposes embedding interpretability across the agent lifecycle — from goal formation through environmental interaction to outcome evaluation. KavachAI implements system-level explainability through multi-layered reasoning capture.

18. **LLM-Driven Explainable AI Pipelines** (arXiv:2511.07086): Presents a modular, explainable LLM-agent pipeline that externalizes reasoning into auditable artifacts. LLM components are paired with deterministic analyzers, yielding traceable intermediates rather than opaque outputs. KavachAI adopts this principle of separating opaque LLM reasoning from transparent, auditable process artifacts.

19. **OpenAgentSafety — Comprehensive Agent Safety Evaluation** (arXiv:2507.06134): A modular framework for evaluating agent behavior across eight critical risk categories. Combines rule-based evaluation with LLM-as-judge assessments to detect both overt and subtle unsafe behaviors. KavachAI implements continuous LLM evaluation inspired by this framework.

20. **Neuro-Symbolic Framework for Safe Agentic AI** (arXiv:2512.20275): Demonstrates a three-layer Governance Triad combining a domain-adapted agent with a Network Knowledge Graph and SHACL constraints. Key finding: even high-performing domain agents require deterministic graph validation to achieve verifiable safety compliance. KavachAI's Semantic Grounding Layer implements this principle of pairing LLM reasoning with deterministic knowledge validation.

[↑ Back to Top](#table-of-contents)

## Glossary

- **KavachAI**: The overall Zero Trust safety firewall system for governing autonomous AI agents
- **Zero_Trust_Engine**: The core component that enforces the principle of "never trust, always verify" — every agent action is authenticated, authorized, and attested regardless of origin
- **Agent_Identity_Manager**: The component responsible for issuing, verifying, and revoking cryptographic agent identities, including scoped credentials and capability tokens
- **Agent_Identity**: A cryptographically verifiable identity bound to an agent instance, containing the agent's public key, capability scope, and trust level
- **Capability_Token**: A scoped, time-limited, cryptographically signed token granting an agent permission to invoke specific tools with specific parameter constraints
- **Action_Attestation**: A cryptographically signed receipt for every executed action, containing the action hash, agent identity, policy evaluation result, and timestamp — forming the basis of the tamper-proof audit trail
- **Policy_Engine**: The component that loads, validates, and evaluates safety policies written in the KavachAI DSL against agent actions
- **KavachAI_DSL**: A domain-specific language for expressing safety policies, supporting temporal logic constraints, information flow policies, and composable policy modules
- **DSL_Parser**: The PEG-based parser that transforms KavachAI DSL source text into an executable policy Abstract Syntax Tree (AST)
- **DSL_Pretty_Printer**: The component that serializes a policy AST back into valid KavachAI DSL source text
- **Temporal_Constraint**: A DSL construct expressing time-based relationships between actions (e.g., "agent must not access resource X within 5 minutes of accessing resource Y")
- **Information_Flow_Policy**: A DSL construct expressing data flow restrictions (e.g., "data from source A must never reach destination B through any chain of actions")
- **Policy_Module**: A composable, reusable unit of DSL policy that can be imported and combined with other modules
- **Action_Interceptor**: The middleware component that hooks into agent tool-calling pipelines across frameworks and inspects every action before execution
- **Action_Request**: A structured representation of an agent's intended tool call, including tool name, parameters, agent identity, session context, and reasoning trace
- **Action_Verdict**: The result of policy evaluation — one of ALLOW, BLOCK, FLAG, ESCALATE, or QUARANTINE
- **QUARANTINE**: An Action_Verdict that isolates the action and the agent session for forensic analysis, triggered by high-confidence attack detection
- **Threat_Detector**: The advanced threat detection engine that identifies prompt injection, tool poisoning, privilege escalation, covert data exfiltration, and multi-step attack chains
- **Prompt_Injection_Detector**: A sub-component of Threat_Detector that identifies direct and indirect prompt injection attempts in agent inputs and tool outputs
- **Tool_Poisoning_Detector**: A sub-component of Threat_Detector that identifies malicious or manipulated tool responses designed to alter agent behavior
- **Privilege_Escalation_Detector**: A sub-component of Threat_Detector that identifies attempts by an agent to access tools or resources beyond its Capability_Token scope
- **Covert_Channel_Detector**: A sub-component of Threat_Detector that identifies steganographic or encoded data hiding in agent outputs intended for data exfiltration
- **Attack_Chain_Analyzer**: A sub-component of Threat_Detector that correlates sequences of individually benign actions to identify collectively malicious multi-step attack patterns
- **Kill_Chain**: A structured representation of a detected multi-step attack, mapping each stage to the MITRE ATT&CK framework for agentic AI
- **Threat_Score**: A numerical score (0.0 to 1.0) representing the assessed threat level of an action or session, computed by the Threat_Detector
- **DPDP_Compliance_Engine**: The component that enforces India's Digital Personal Data Protection Act 2023, including consent verification, data localization, breach notification, and PII masking
- **Consent_Record**: A verifiable record that data processing consent was obtained from the data principal before the agent processes personal data
- **Data_Localization_Rule**: A configurable rule specifying that certain categories of personal data must not be transmitted outside India's jurisdiction
- **Breach_Notification_Trigger**: An automated mechanism that detects potential data breaches and initiates notification workflows per DPDP Act timelines
- **PII_Masker**: The component that detects and masks Indian PII patterns including Aadhaar numbers, PAN numbers, mobile numbers, and UPI IDs in agent data flows
- **Cryptographic_Audit_Trail**: A tamper-proof log where each entry is cryptographically linked to the previous entry via hash chaining, producing evidence-grade records
- **Hash_Chain**: The data structure underlying the Cryptographic_Audit_Trail, where each log entry contains the SHA-256 hash of the previous entry, making retroactive tampering detectable
- **Audit_Entry**: A single record in the Cryptographic_Audit_Trail containing timestamp, action details, policy evaluation, threat assessment, agent identity, previous entry hash, and the entry's own hash
- **Chain_of_Custody**: A verifiable sequence of Audit_Entries documenting every handler and decision point for an agent action, suitable for legal proceedings
- **Evidence_Package**: An exportable, cryptographically signed bundle of Audit_Entries for a specific incident, formatted for law enforcement submission
- **Multi_Agent_Governor**: The component that monitors and governs interactions between multiple agents in a multi-agent system
- **Delegation_Chain**: A tracked sequence of task delegations between agents, recording which agent delegated what task to which other agent, with what permissions
- **Collusion_Detector**: A sub-component of Multi_Agent_Governor that identifies coordinated behavior between agents that circumvents individual safety policies
- **Inter_Agent_Monitor**: A sub-component of Multi_Agent_Governor that inspects messages and data exchanged between agents for policy compliance
- **SOC_Dashboard**: The Security Operations Center style React dashboard providing real-time threat visualization, compliance monitoring, and forensic investigation
- **Kill_Chain_View**: A dashboard visualization that maps detected attack stages to a timeline, showing the progression and interdependencies of a multi-step attack
- **Compliance_Posture**: A dashboard view showing the current state of DPDP Act compliance across all active agent sessions
- **Forensic_Mode**: A dashboard capability that enables deep-dive investigation of past incidents with full action replay and evidence export
- **Escalation_Manager**: The component that routes high-risk actions to human operators for approval, with configurable timeouts and safe defaults
- **Escalation_Timeout**: The configurable duration after which an escalated action defaults to a safe fallback if no human response is received
- **Safe_Default**: The preconfigured fallback action taken when an Escalation_Timeout expires without human response
- **Incident_Report**: An auto-generated structured report summarizing a security incident, suitable for CERT-In submission and internal review
- **CERT_In_Reporter**: The component that formats and prepares incident data for submission to India's Computer Emergency Response Team
- **SDK**: The Python software development kit providing programmatic access to KavachAI's capabilities for integration with any agent framework
- **Framework_Adapter**: A pluggable adapter that translates framework-specific tool call patterns (LangChain, CrewAI, AutoGen) into KavachAI's canonical Action_Request format
- **Trigger_Predicate_Enforcement**: The core policy evaluation pattern adopted from AgentSpec research — a trigger condition activates evaluation, a predicate checks the constraint, and an enforcement action is applied (ALLOW, BLOCK, FLAG, ESCALATE, QUARANTINE)
- **LTL_Operator**: A Linear Temporal Logic operator supported by the KavachAI DSL for expressing temporal behavioral constraints — includes ALWAYS (globally true), EVENTUALLY (true at some future point), UNTIL (true until another condition holds), and NEXT (true at the next action step)
- **Probabilistic_Rule_Circuit**: A directed acyclic graph of policy rules with associated probability weights, constructed from DSL policies by the Policy_Engine for efficient evaluation — inspired by ShieldAgent research
- **Formal_Policy_Verifier**: The component that performs offline formal verification of KavachAI DSL policies before deployment, proving correctness properties such as consistency, completeness, and absence of conflicting rules
- **Runtime_Policy_Monitor**: The lightweight online component that validates each agent action against pre-verified policies during execution, providing formal safety guarantees with minimal overhead
- **DFA_Behavioral_Model**: A Deterministic Finite Automaton encoding valid agent workflows as states (agent contexts) and transitions (tool calls), used by the runtime engine to verify that agent tool-call sequences follow valid paths
- **DFA_State**: A node in the DFA_Behavioral_Model representing a valid agent context (e.g., "authenticated", "data_accessed", "payment_initiated")
- **DFA_Transition**: An edge in the DFA_Behavioral_Model representing a valid tool call that moves the agent from one DFA_State to another
- **Path_Correctness**: A DFA-based metric measuring whether an agent's complete tool-call sequence follows a valid path from start state to an accepting state in the DFA_Behavioral_Model
- **Harmful_Call_Rate**: A DFA-based metric measuring the proportion of agent tool calls that transition to invalid or dangerous states in the DFA_Behavioral_Model
- **Prefix_Criticality**: A DFA-based metric measuring how early in an action sequence a deviation from valid DFA paths occurs — earlier deviations indicate higher risk
- **Trust_Score**: A dynamic numerical score (0.0 to 1.0) assigned to each agent based on cumulative compliance history, severity-weighted violations, and time-based decay — modulates the strictness of policy enforcement
- **Trust_Level**: A categorical classification derived from Trust_Score — one of TRUSTED (0.8-1.0), STANDARD (0.5-0.79), RESTRICTED (0.2-0.49), or QUARANTINED (0.0-0.19)
- **Trust_Decay**: The mechanism by which an agent's Trust_Score gradually decreases during periods of inactivity, requiring re-establishment of trust through compliant behavior
- **Graduated_Enforcement**: A policy enforcement strategy where the strictness of enforcement scales with the agent's Trust_Level — trusted agents receive lighter monitoring, restricted agents face stricter controls
- **Trajectory_Determinism**: A measure of whether an agent produces the same sequence of tool calls when given identical inputs across multiple runs — critical for regulatory audit replay
- **Decision_Determinism**: A measure of whether an agent produces the same final decision or output when given identical inputs — measured independently from Trajectory_Determinism per DFAH research findings
- **Determinism_Report**: A structured report comparing agent behavior across identical input replays, documenting trajectory and decision determinism scores for regulatory audit purposes
- **STAC_Attack**: A Sequential Tool Attack Chain where individually harmless tool calls are chained together to collectively enable harmful operations — a threat vector validated by STAC research with 90%+ attack success rates against SOTA agents
- **MCP**: Model Context Protocol — an open standard (JSON-RPC 2.0) defining how AI agents communicate with external tools, data sources, and services. KavachAI operates as an MCP proxy gateway.
- **MCP_Proxy_Gateway**: KavachAI's core integration architecture — a transparent proxy that sits between MCP clients (AI agents) and MCP servers (tools), intercepting all tool calls for governance evaluation before forwarding to the actual tool server.
- **MCP_Client**: An AI agent or application that connects to MCP servers to invoke tools (e.g., Claude Desktop, LangChain MCP agent, custom agents).
- **MCP_Server**: A service that exposes tools, resources, and prompts via the MCP protocol (e.g., file system server, database server, API server).
- **MCP_Safety_Server**: An MCP server exposed by KavachAI that provides safety-related tools to agents — allowing agents to proactively query their own safety constraints, check policies, and request escalations.
- **Tool_Call_Intercept**: The mechanism by which the MCP_Proxy_Gateway captures a tools/call JSON-RPC request from an MCP_Client before forwarding it to the target MCP_Server.
- **Tool_Discovery_Filter**: The mechanism by which the MCP_Proxy_Gateway filters the tools/list response from MCP_Servers, hiding tools that the agent's Capability_Token does not authorize.
- **Capability_Label**: A structured metadata label attached to MCP tool definitions specifying the tool's capability category, confidentiality level, and required trust level — inspired by the capability-enhanced MCP framework (arXiv:2601.08012).
- **LLM_Gateway**: The component that provides a unified interface for routing agent LLM requests to multiple model providers (OpenAI, Anthropic, Google, open-source), with provider-agnostic safety governance, cost tracking, and fallback routing.
- **Model_Profile**: A configuration defining the risk characteristics, capability level, cost tier, and safety constraints for a specific LLM model — used by the LLM_Gateway to apply model-appropriate governance.
- **LLM_Request_Interceptor**: The component that intercepts agent-to-LLM requests (prompts, completions) for safety scanning before they reach the LLM provider, and scans LLM responses before they reach the agent.
- **Ethics_Engine**: The component responsible for detecting and mitigating ethical risks in agent behavior, including bias, toxicity, fairness violations, and content safety issues.
- **Bias_Detector**: A sub-component of Ethics_Engine that identifies biased content in agent outputs, with configurable sensitivity for India-specific bias categories (gender, caste, religion, regional, linguistic).
- **Toxicity_Filter**: A sub-component of Ethics_Engine that detects and blocks toxic, harmful, or inappropriate content in agent inputs and outputs.
- **Hallucination_Detector**: A sub-component that identifies when an agent fabricates tool executions, misstates results, or presents inferences as verified facts — validated against Action_Attestation records.
- **Fairness_Monitor**: A sub-component of Ethics_Engine that tracks agent behavior patterns across interactions to detect systematic unfairness or discriminatory patterns.
- **Content_Safety_Classifier**: A sub-component that classifies agent outputs against configurable content safety categories (violence, self-harm, illegal activity, misinformation).
- **Ethics_Score**: A numerical score (0.0 to 1.0) representing the ethical compliance of an agent's behavior across bias, toxicity, fairness, and content safety dimensions.
- **India_AI_Governance_Mapper**: A component that maps KavachAI's capabilities to the seven principles of India's AI Governance Guidelines 2025, generating compliance reports.
- **Seven_Sutras_Compliance**: A structured assessment of how an agent session aligns with India's seven AI governance principles.
- **LLM_Budget**: A configurable spending limit for LLM API usage per agent, session, or organization, enforced by the LLM_Gateway.
- **Model_Fallback_Chain**: An ordered list of LLM models that the LLM_Gateway will try in sequence if the primary model is unavailable or returns an error.
- **Output_Validator**: The component that validates agent outputs against grounding sources, tool receipts, and factual consistency checks before the output reaches the end user.
- **LLM_Reasoning_Capture**: The mechanism by which KavachAI captures, stores, and makes auditable the LLM's chain-of-thought reasoning that led to each agent action — including the prompt, the model's reasoning steps, and the final decision.
- **Decision_Explanation**: A structured, multi-layered explanation of an agent decision containing: (1) the LLM's reasoning chain (why the agent decided to take this action), (2) the policy evaluation result (why KavachAI allowed/blocked it), and (3) a user-facing plain-language summary suitable for affected individuals.
- **Model_Card**: A structured documentation artifact for each LLM model used by the LLM_Gateway, containing the model's name, version, provider, known limitations, bias evaluations, training data provenance summary, and performance benchmarks.
- **Model_Provenance_Record**: A per-action record in the Cryptographic_Audit_Trail documenting which specific LLM model (name, version, provider, temperature setting) generated the reasoning that led to the agent's action.
- **User_Facing_Explanation**: A plain-language explanation of an agent decision generated for the individual affected by the decision, suitable for "right to explanation" compliance under DPDP Act and EU AI Act.
- **Explanation_Template**: A configurable template that defines how Decision_Explanations are formatted for different audiences (technical auditors, compliance officers, affected individuals, policy makers).
- **LLM_Observability**: The component that monitors LLM performance metrics including response latency, token usage, error rates, response quality scores, and model drift indicators across all models in the LLM_Gateway.
- **Model_Drift_Detector**: A sub-component of LLM_Observability that detects when an LLM model's behavior changes over time (e.g., increased refusal rates, quality degradation, bias shifts) by comparing current performance against baseline metrics.
- **Tenant**: An isolated organizational unit within KavachAI, with its own policies, agents, budgets, audit trails, and compliance configurations — enabling multi-tenant deployment.
- **Tenant_Isolation**: The security boundary ensuring that agents, policies, audit data, and LLM configurations belonging to one Tenant cannot be accessed by another Tenant.
- **LLM_Eval_Engine**: The component that systematically evaluates LLM models against safety, accuracy, bias, and domain-specific benchmarks before deployment and continuously during operation.
- **Safety_Benchmark**: A configurable test suite containing adversarial prompts, bias probes, and domain-specific evaluation cases used by the LLM_Eval_Engine to score LLM models.
- **Model_Safety_Score**: A composite score (0-100) computed by the LLM_Eval_Engine for each LLM model, aggregating safety, accuracy, bias, and compliance sub-scores.
- **Red_Team_Runner**: A sub-component of LLM_Eval_Engine that automatically generates and executes adversarial test cases against LLM models to probe for vulnerabilities.
- **Semantic_Grounding_Layer**: The deterministic validation layer that grounds agent decisions and outputs in verified knowledge sources — including knowledge graphs, domain ontologies, structured schemas, and retrieved documents — ensuring that agent claims are traceable to authoritative data rather than relying solely on LLM parametric knowledge.
- **Knowledge_Graph**: A structured graph of domain-specific entities, relationships, and facts used by the Semantic_Grounding_Layer to validate agent claims against verified knowledge.
- **Domain_Ontology**: A formal specification of concepts, properties, and relationships within a specific domain (e.g., financial services, healthcare) used by the Semantic_Grounding_Layer to enforce semantic correctness of agent outputs.
- **Schema_Enforcer**: A sub-component of the Semantic_Grounding_Layer that validates agent outputs against predefined JSON schemas, ensuring structured and predictable output formats.
- **Grounding_Score**: A numerical score (0.0 to 1.0) measuring the proportion of an agent's output claims that are traceable to verified knowledge sources in the Semantic_Grounding_Layer.
- **Source_Attribution**: A structured reference linking each claim in an agent's output to the specific knowledge source (document, knowledge graph node, tool response) that supports it.
- **Deterministic_Validator**: A non-LLM component that performs rule-based, schema-based, and graph-based validation of agent outputs — providing verification that does not depend on probabilistic LLM judgment.

[↑ Back to Top](#table-of-contents)

## Requirements

### Requirement 1: Zero Trust Agent Identity and Authentication

**User Story:** As a security architect, I want every AI agent to possess a cryptographically verifiable identity with scoped credentials, so that no agent action is implicitly trusted and every action can be attributed to a verified source.

#### Acceptance Criteria

1. WHEN an agent registers with KavachAI, THE Agent_Identity_Manager SHALL issue an Agent_Identity containing a unique identifier, an Ed25519 public/private key pair, a capability scope definition, and a trust level classification.
2. WHEN an agent submits an Action_Request, THE Zero_Trust_Engine SHALL verify the agent's cryptographic signature on the request before any policy evaluation occurs.
3. IF an Action_Request contains an invalid or expired cryptographic signature, THEN THE Zero_Trust_Engine SHALL reject the request with an AUTHENTICATION_FAILED error and record the rejection in the Cryptographic_Audit_Trail.
4. THE Agent_Identity_Manager SHALL issue Capability_Tokens that are scoped to specific tools, parameter value ranges, resource paths, and time windows.
5. WHEN an agent attempts to invoke a tool not listed in the agent's active Capability_Token, THE Zero_Trust_Engine SHALL return a BLOCK verdict with a PRIVILEGE_VIOLATION reason.
6. THE Agent_Identity_Manager SHALL support revocation of Agent_Identities and Capability_Tokens, with revocation taking effect within 1 second across all KavachAI components.
7. WHEN a Capability_Token expires, THE Zero_Trust_Engine SHALL reject all subsequent Action_Requests using that token until a new token is issued.
8. THE Zero_Trust_Engine SHALL enforce least-privilege by default — agents receive the minimum Capability_Token scope required for their declared task.

[↑ Back to Top](#table-of-contents)

### Requirement 2: KavachAI DSL — Formal Policy Language

**User Story:** As a security policy author, I want to express complex safety policies in a formal domain-specific language with temporal logic, information flow constraints, and research-backed enforcement patterns, so that policies are precise, composable, verifiable, and accessible to authors without deep formal methods expertise.

#### Acceptance Criteria

1. THE DSL_Parser SHALL parse KavachAI DSL source text into a policy AST using a PEG-based grammar.
2. THE KavachAI_DSL SHALL support the following constraint types: action-level constraints (allow/block specific tool calls), Temporal_Constraints (time-based relationships between actions), Information_Flow_Policies (data flow restrictions across action chains), rate limits (frequency bounds per time window), and threshold-based escalation rules.
3. WHEN a Temporal_Constraint specifies "agent must not access resource X within T minutes of accessing resource Y", THE Policy_Engine SHALL track the timestamps of relevant actions per agent session and enforce the constraint.
4. WHEN an Information_Flow_Policy specifies "data from source A must not reach destination B", THE Policy_Engine SHALL track data provenance across action chains within a session and block any action that would violate the flow restriction.
5. THE KavachAI_DSL SHALL support Policy_Module imports, allowing policy authors to compose policies from reusable modules using an "import" directive.
6. THE DSL_Pretty_Printer SHALL format policy AST nodes back into valid, human-readable KavachAI DSL source text.
7. FOR ALL valid KavachAI DSL source texts, parsing via DSL_Parser then printing via DSL_Pretty_Printer then parsing again SHALL produce an equivalent policy AST (round-trip property).
8. IF the DSL_Parser encounters a syntax error, THEN THE DSL_Parser SHALL return an error message containing the line number, column number, and a description of the expected token.
9. THE KavachAI_DSL SHALL support parameterized policy templates that accept configuration values (e.g., threshold amounts, time windows, resource lists) at instantiation time.
10. THE Policy_Engine SHALL evaluate a single policy rule against an Action_Request within 10 milliseconds.
11. THE KavachAI_DSL SHALL adopt the Trigger_Predicate_Enforcement pattern inspired by AgentSpec (arXiv:2503.18666), where each policy rule consists of: (a) a trigger condition that activates evaluation (e.g., tool call event, state change), (b) a predicate that checks the constraint (e.g., parameter validation, scope check), and (c) an enforcement action (ALLOW, BLOCK, FLAG, ESCALATE, or QUARANTINE).
12. THE KavachAI_DSL SHALL support Linear Temporal Logic (LTL) operators inspired by temporal logic for agent correctness (arXiv:2509.20364): ALWAYS (a property holds at every step in the execution trace), EVENTUALLY (a property holds at some future step), UNTIL (a property holds until another property becomes true), and NEXT (a property holds at the immediately following action step).
13. WHEN a policy rule uses LTL_Operators, THE Policy_Engine SHALL evaluate the operators against the agent's execution trace (sequence of tool calls and state transitions) rather than individual text content, enabling behavioral pattern monitoring across execution scenarios.
14. THE Policy_Engine SHALL construct Probabilistic_Rule_Circuits from KavachAI DSL policies, inspired by ShieldAgent (arXiv:2503.22738), organizing policy rules into directed acyclic graphs with associated probability weights for efficient evaluation.
15. WHEN evaluating an Action_Request, THE Policy_Engine SHALL traverse the Probabilistic_Rule_Circuit to determine the applicable rules and compute a weighted policy compliance score, reducing redundant rule evaluations.
16. THE KavachAI_DSL SHALL use human-readable, plain-English-like syntax for all constructs including LTL operators and trigger-predicate-enforcement patterns, so that policy authors without formal methods training can write and understand policies. Accessibility note: the DSL documentation SHALL include annotated examples for every construct, and the SOC_Dashboard SHALL provide a visual policy builder as an alternative to raw DSL authoring.

[↑ Back to Top](#table-of-contents)

### Requirement 3: Advanced Threat Detection Engine

**User Story:** As a cybersecurity analyst, I want KavachAI to detect sophisticated attack vectors including prompt injection, tool poisoning, privilege escalation, covert data exfiltration, sequential tool attack chains (STAC), and multi-step attack chains, so that agents are protected against adversarial threats beyond simple policy violations.

#### Acceptance Criteria

1. WHEN an Action_Request or tool output contains patterns indicative of indirect prompt injection (e.g., embedded instructions in tool-returned data attempting to override agent behavior), THE Prompt_Injection_Detector SHALL flag the content with a Threat_Score and the specific injection pattern identified.
2. WHEN a tool response contains data that deviates significantly from the expected schema or statistical profile for that tool, THE Tool_Poisoning_Detector SHALL flag the response as potentially poisoned and assign a Threat_Score.
3. WHEN an agent issues a sequence of Action_Requests that progressively expand the agent's effective access scope beyond the original Capability_Token, THE Privilege_Escalation_Detector SHALL identify the escalation pattern and issue a QUARANTINE verdict.
4. WHEN an agent's outbound data contains steganographic encoding, unusual character sequences, or base64-encoded payloads not consistent with the declared action purpose, THE Covert_Channel_Detector SHALL flag the action as a potential data exfiltration attempt.
5. WHEN a sequence of individually ALLOW-verdict actions matches a known multi-step attack pattern (e.g., reconnaissance → data access → encoding → exfiltration), THE Attack_Chain_Analyzer SHALL correlate the actions into a Kill_Chain and escalate the session.
6. THE Attack_Chain_Analyzer SHALL maintain a sliding window of the last 50 actions per session for pattern correlation.
7. WHEN a Kill_Chain is detected, THE Threat_Detector SHALL generate a structured Kill_Chain object mapping each attack stage to a category (reconnaissance, weaponization, delivery, exploitation, exfiltration, command-and-control).
8. THE Threat_Detector SHALL compute a session-level Threat_Score by aggregating individual action Threat_Scores using a weighted decay function that gives higher weight to recent actions.
9. WHEN a session-level Threat_Score exceeds a configurable threshold (default 0.8), THE Threat_Detector SHALL trigger automatic session QUARANTINE and notify the SOC_Dashboard.
10. THE Threat_Detector SHALL evaluate each action within 50 milliseconds, excluding network-dependent checks.
11. THE Attack_Chain_Analyzer SHALL explicitly defend against STAC-style Sequential Tool Attack Chains (arXiv:2509.25624), where individually harmless tool calls are chained together to collectively enable harmful operations — a threat vector with demonstrated 90%+ attack success rates against SOTA agents.
12. WHEN evaluating an Action_Request, THE Attack_Chain_Analyzer SHALL apply reasoning-driven defense by evaluating the cumulative effects of the current action in the context of all preceding actions in the session, rather than evaluating each action in isolation.
13. THE Attack_Chain_Analyzer SHALL maintain a cumulative effect model per session that tracks the aggregate state changes, data flows, and permission usage across all actions, enabling detection of STAC_Attacks where each individual action appears benign but the cumulative sequence achieves a harmful objective.
14. WHEN the Attack_Chain_Analyzer detects a STAC_Attack pattern, THE Attack_Chain_Analyzer SHALL generate a STAC-specific Kill_Chain object that identifies the individually benign actions, the cumulative harmful effect, and the point at which the chain became harmful.

[↑ Back to Top](#table-of-contents)

### Requirement 4: DPDP Act 2023 Compliance Engine

**User Story:** As a compliance officer operating in India, I want KavachAI to enforce Digital Personal Data Protection Act 2023 requirements automatically, so that AI agent operations comply with Indian data protection law without manual oversight.

#### Acceptance Criteria

1. WHEN an agent processes personal data, THE DPDP_Compliance_Engine SHALL verify that a valid Consent_Record exists for the data principal and the specific processing purpose before allowing the action.
2. IF an Action_Request involves processing personal data without a valid Consent_Record, THEN THE DPDP_Compliance_Engine SHALL block the action and record a CONSENT_VIOLATION in the Cryptographic_Audit_Trail.
3. WHEN an Action_Request would transmit personal data to a destination outside India, THE DPDP_Compliance_Engine SHALL evaluate the destination against configured Data_Localization_Rules and block the transmission if the data category requires localization.
4. THE PII_Masker SHALL detect and mask Aadhaar numbers (12-digit format with optional spaces), PAN numbers (ABCDE1234F format), Indian mobile numbers (+91 prefix, 10-digit), UPI IDs (name@bank format), and email addresses in all agent data flows.
5. WHEN the PII_Masker detects Aadhaar numbers in agent data, THE PII_Masker SHALL replace the numbers with a masked format showing only the last 4 digits (e.g., "XXXX XXXX 1234").
6. WHEN the DPDP_Compliance_Engine detects a potential data breach (unauthorized access to personal data, exfiltration attempt, or policy bypass), THE Breach_Notification_Trigger SHALL generate a breach alert within 1 second containing the breach type, affected data categories, estimated scope, and recommended response actions.
7. THE DPDP_Compliance_Engine SHALL maintain a processing register that records all personal data processing activities by agents, including purpose, legal basis, data categories, and retention period.
8. THE DPDP_Compliance_Engine SHALL support configurable data retention policies that automatically flag or delete personal data held beyond the specified retention period.
9. WHEN a data principal exercises the right to erasure, THE DPDP_Compliance_Engine SHALL identify all Audit_Entries and cached data containing the data principal's personal data and mark the entries for redaction while preserving the Hash_Chain integrity.

[↑ Back to Top](#table-of-contents)

### Requirement 5: Action Interception and Zero Trust Evaluation Pipeline

**User Story:** As a safety engineer, I want every agent tool call to pass through a Zero Trust evaluation pipeline that authenticates, authorizes, scans for threats, checks compliance, and attests the result, so that no unsafe action can bypass governance.

#### Acceptance Criteria

1. WHEN an AI agent issues a tool call, THE Action_Interceptor SHALL capture the Action_Request before the tool executes, regardless of the agent framework in use.
2. THE Action_Interceptor SHALL execute the following evaluation pipeline in order: (1) authenticate agent identity, (2) verify Capability_Token scope, (3) evaluate KavachAI DSL policies, (4) run Threat_Detector analysis, (5) check DPDP_Compliance_Engine rules, (6) run Ethics_Engine evaluation, (7) apply PII_Masker if needed, (8) capture LLM_Reasoning via LLM_Reasoning_Capture, (9) validate output via Semantic_Grounding_Layer, (10) generate Action_Attestation.
3. WHEN any pipeline stage returns a BLOCK, ESCALATE, or QUARANTINE verdict, THE Action_Interceptor SHALL halt the pipeline and return the verdict immediately without executing subsequent stages.
4. WHEN the full pipeline returns an ALLOW verdict, THE Action_Interceptor SHALL generate an Action_Attestation signed with KavachAI's private key, containing the action hash, agent identity, all policy evaluation results, and a timestamp.
5. THE Action_Interceptor SHALL add less than 100 milliseconds of total latency to each tool call under normal operating conditions (excluding escalation wait time).
6. WHEN the Policy_Engine returns a FLAG verdict, THE Action_Interceptor SHALL permit the tool call, generate the Action_Attestation, and record a warning with the Threat_Score in the Cryptographic_Audit_Trail.
7. WHEN the Action_Interceptor receives a QUARANTINE verdict, THE Action_Interceptor SHALL block the current action, suspend the agent session, preserve all session state for forensic analysis, and notify the SOC_Dashboard.
8. THE Action_Interceptor SHALL support concurrent evaluation of Action_Requests from multiple agent sessions without cross-session data leakage.

[↑ Back to Top](#table-of-contents)

### Requirement 6: Cryptographic Audit Trail and Evidence Chain

**User Story:** As a law enforcement investigator, I want agent activity logs that are tamper-proof, cryptographically verifiable, and admissible as digital evidence, so that agent actions can be investigated and presented in legal proceedings.

#### Acceptance Criteria

1. THE Cryptographic_Audit_Trail SHALL store each Audit_Entry in a SQLite database with the following fields: entry_id, timestamp, session_id, agent_identity_hash, action_type, action_parameters_hash, action_verdict, matched_policies, threat_score, previous_entry_hash, and entry_hash.
2. THE Cryptographic_Audit_Trail SHALL compute each entry_hash as SHA-256(entry_id || timestamp || session_id || agent_identity_hash || action_parameters_hash || action_verdict || previous_entry_hash).
3. WHEN a new Audit_Entry is appended, THE Cryptographic_Audit_Trail SHALL set the previous_entry_hash to the entry_hash of the immediately preceding entry in the same session chain.
4. THE Cryptographic_Audit_Trail SHALL support integrity verification by recomputing the hash chain from any starting entry and comparing against stored hashes.
5. IF a hash chain verification detects a mismatch (indicating tampering), THEN THE Cryptographic_Audit_Trail SHALL report the first tampered entry_id, the expected hash, and the actual hash.
6. THE Cryptographic_Audit_Trail SHALL support exporting an Evidence_Package for a specified session or time range, containing all Audit_Entries, the hash chain verification proof, and a digital signature over the entire package.
7. THE Evidence_Package SHALL include a Chain_of_Custody section documenting every system component that handled each action, with timestamps and component identity hashes.
8. THE Cryptographic_Audit_Trail SHALL assign monotonically increasing sequence numbers to entries within each session to detect deletion attacks.
9. IF the Cryptographic_Audit_Trail fails to persist an Audit_Entry, THEN THE Cryptographic_Audit_Trail SHALL retry the write operation up to 3 times, and if all retries fail, THE Cryptographic_Audit_Trail SHALL halt the agent session to prevent unaudited actions.

[↑ Back to Top](#table-of-contents)

### Requirement 7: Multi-Agent Governance

**User Story:** As a platform operator running multi-agent systems, I want KavachAI to monitor and govern interactions between multiple agents, so that coordinated attacks, unauthorized delegation, and collusion between agents are detected and prevented.

#### Acceptance Criteria

1. WHEN an agent delegates a task to another agent, THE Multi_Agent_Governor SHALL record the Delegation_Chain entry containing the delegating agent identity, the receiving agent identity, the delegated task description, and the permission scope transferred.
2. THE Multi_Agent_Governor SHALL enforce that a delegating agent cannot grant permissions exceeding the delegating agent's own Capability_Token scope (no privilege amplification through delegation).
3. WHEN the Inter_Agent_Monitor detects a message between agents, THE Inter_Agent_Monitor SHALL evaluate the message content against the KavachAI DSL policies applicable to inter-agent communication.
4. WHEN two or more agents exhibit a coordinated pattern of actions that individually comply with policies but collectively violate a safety constraint (e.g., one agent reads sensitive data and passes it to another agent that exfiltrates it), THE Collusion_Detector SHALL flag the pattern and escalate the involved sessions.
5. THE Collusion_Detector SHALL maintain a cross-session action graph linking actions across agent sessions that share data or causal dependencies.
6. WHEN a Delegation_Chain exceeds a configurable maximum depth (default 3), THE Multi_Agent_Governor SHALL block further delegation and escalate to the SOC_Dashboard.
7. THE Multi_Agent_Governor SHALL enforce that each agent in a multi-agent system has a distinct Agent_Identity and cannot impersonate another agent.
8. THE Multi_Agent_Governor SHALL record all inter-agent communications in the Cryptographic_Audit_Trail with both sender and receiver agent identity hashes.

[↑ Back to Top](#table-of-contents)

### Requirement 8: Human-in-the-Loop Escalation with Forensic Context

**User Story:** As a security operations analyst, I want escalated actions to arrive with full forensic context including threat analysis, kill chain position, and compliance impact, so that I can make informed approval or rejection decisions rapidly.

#### Acceptance Criteria

1. WHEN an Action_Request is escalated, THE Escalation_Manager SHALL send a notification to the SOC_Dashboard containing the Action_Request details, matched Policy_Rules, Threat_Score, Kill_Chain context (if applicable), DPDP compliance impact assessment, and the agent's Capability_Token scope.
2. WHEN a human operator approves an escalated Action_Request via the SOC_Dashboard, THE Escalation_Manager SHALL instruct the Action_Interceptor to execute the tool call and record the human decision with the operator's identity in the Cryptographic_Audit_Trail.
3. WHEN a human operator rejects an escalated Action_Request, THE Escalation_Manager SHALL instruct the Action_Interceptor to block the tool call, return a denial message to the agent, and record the rejection with the operator's stated reason.
4. WHEN an Escalation_Timeout expires without a human response, THE Escalation_Manager SHALL apply the configured Safe_Default action (default: BLOCK) and record the timeout event.
5. THE Escalation_Manager SHALL support configurable Escalation_Timeout values per policy rule, with a system-wide default of 60 seconds.
6. WHILE an Action_Request is pending human approval, THE Escalation_Manager SHALL prevent the agent from issuing duplicate requests for the same action and SHALL prevent the agent from issuing actions that depend on the pending action's result.
7. THE Escalation_Manager SHALL prioritize escalation notifications by Threat_Score, displaying higher-threat escalations more prominently on the SOC_Dashboard.

[↑ Back to Top](#table-of-contents)

### Requirement 9: SOC-Style Real-Time Threat Intelligence Dashboard

**User Story:** As a security operations analyst, I want a Security Operations Center style dashboard with live threat scoring, attack visualization, compliance monitoring, and forensic investigation capabilities, so that I can monitor, investigate, and respond to agent security events in real time.

#### Acceptance Criteria

1. THE SOC_Dashboard SHALL display a live threat feed showing all active agent sessions with their current session-level Threat_Scores, updated within 2 seconds of each action.
2. THE SOC_Dashboard SHALL provide a Kill_Chain_View that visualizes detected multi-step attacks as a directed graph, mapping each attack stage to its category and showing the temporal progression.
3. THE SOC_Dashboard SHALL display a Compliance_Posture overview showing DPDP Act compliance status across all active sessions, including consent verification status, data localization compliance, and PII masking coverage.
4. THE SOC_Dashboard SHALL provide policy effectiveness metrics showing the number of actions evaluated, verdicts issued (ALLOW, BLOCK, FLAG, ESCALATE, QUARANTINE), and the top 10 most-triggered policy rules over configurable time windows.
5. WHEN a user activates Forensic_Mode for a specific session, THE SOC_Dashboard SHALL display the complete action timeline with full Reasoning_Traces, Threat_Scores, policy evaluations, and the ability to replay the session action-by-action.
6. THE SOC_Dashboard SHALL provide a session comparison view that displays two agent sessions side-by-side for behavioral comparison during investigation.
7. WHEN a user selects an action in the timeline, THE SOC_Dashboard SHALL display the Action_Attestation, the agent's Capability_Token scope at the time of the action, and any related Kill_Chain context.
8. THE SOC_Dashboard SHALL provide a real-time alert panel that displays QUARANTINE events, high-severity escalations, and hash chain integrity violations with audio/visual notification.
9. THE SOC_Dashboard SHALL support exporting the current dashboard view as a PDF report and exporting session data as an Evidence_Package.
10. THE SOC_Dashboard SHALL display the Delegation_Chain graph for multi-agent sessions, showing which agents delegated tasks to which other agents and the permission scopes transferred.

[↑ Back to Top](#table-of-contents)

### Requirement 10: Law Enforcement Integration and Incident Reporting

**User Story:** As a law enforcement officer investigating AI-related cybercrime, I want evidence-grade audit trails, automated incident reports, and CERT-In compatible reporting, so that agent security incidents can be investigated and prosecuted using legally admissible evidence.

#### Acceptance Criteria

1. WHEN a security incident is detected (session QUARANTINE, Kill_Chain detection, or DPDP breach), THE CERT_In_Reporter SHALL auto-generate an Incident_Report containing: incident type, timestamp, affected systems, attack vector description, impacted data categories, containment actions taken, and recommended remediation steps.
2. THE Incident_Report SHALL follow the CERT-In incident reporting format, including fields for incident category, severity, affected IP ranges, and point of contact.
3. THE Evidence_Package SHALL include cryptographic proof of integrity (hash chain verification), timestamps from a trusted source, and digital signatures that can be independently verified without access to the KavachAI system.
4. THE Cryptographic_Audit_Trail SHALL support Chain_of_Custody queries that return the complete sequence of system components that processed a specific action, with timestamps and component identity verification.
5. WHEN a law enforcement officer requests an Evidence_Package for a specific time range and agent session, THE KavachAI SHALL generate the package within 30 seconds for sessions containing up to 10,000 Audit_Entries.
6. THE Incident_Report SHALL include a human-readable narrative summary of the incident suitable for non-technical stakeholders, generated from the structured incident data.
7. THE KavachAI SHALL provide webhook integration hooks for forwarding incident alerts to external Security Information and Event Management (SIEM) systems and CERT-In reporting portals.

[↑ Back to Top](#table-of-contents)

### Requirement 11: Framework-Agnostic SDK and REST API

**User Story:** As a developer building AI agents on any framework, I want a Python SDK and REST API that integrates KavachAI with LangChain, CrewAI, AutoGen, and custom agent frameworks, so that safety governance is not locked to a single ecosystem.

#### Acceptance Criteria

1. THE SDK SHALL provide Framework_Adapters for LangChain, CrewAI, and AutoGen that translate each framework's tool call mechanism into KavachAI's canonical Action_Request format.
2. THE SDK SHALL provide a generic Framework_Adapter base class that developers can extend to integrate custom agent frameworks with KavachAI using fewer than 20 lines of framework-specific code.
3. THE KavachAI SHALL expose a POST /api/v1/evaluate endpoint that accepts an Action_Request (containing agent_id, tool_name, parameters, session_id, and a cryptographic signature) and returns an Action_Verdict with Reasoning_Trace, Threat_Score, and Action_Attestation.
4. THE KavachAI SHALL expose a GET /api/v1/sessions/{session_id}/threat-profile endpoint that returns the session's current Threat_Score, detected Kill_Chains, and compliance status.
5. THE KavachAI SHALL expose a GET /api/v1/sessions/{session_id}/audit-trail endpoint that returns the Cryptographic_Audit_Trail entries for the session with hash chain verification status.
6. THE KavachAI SHALL expose a POST /api/v1/escalations/{escalation_id}/resolve endpoint that accepts a human operator's approve or reject decision with an optional reason.
7. THE KavachAI SHALL expose a POST /api/v1/agents/register endpoint that registers a new agent and returns an Agent_Identity with a Capability_Token.
8. THE KavachAI SHALL expose a PUT /api/v1/policies endpoint that accepts KavachAI DSL source text and triggers a hot reload of policies within 5 seconds.
9. THE KavachAI SHALL expose a GET /api/v1/compliance/dpdp-status endpoint that returns the current DPDP Act compliance posture across all active sessions.
10. IF an API request contains an invalid or missing X-API-Key header, THEN THE KavachAI SHALL return HTTP 401 with an error message and record the unauthorized access attempt in the Cryptographic_Audit_Trail.
11. IF an API request contains malformed JSON or missing required fields, THEN THE KavachAI SHALL return HTTP 400 with a descriptive error message identifying the validation failures.
12. WHEN the LangChain Framework_Adapter is added to a LangChain agent, THE adapter SHALL integrate with 5 or fewer lines of configuration code.

[↑ Back to Top](#table-of-contents)

### Requirement 12: FastAPI Backend Infrastructure

**User Story:** As a DevOps engineer, I want the KavachAI backend to be a robust FastAPI application with Redis-backed real-time state management, so that the system can handle concurrent agent sessions with low latency.

#### Acceptance Criteria

1. THE KavachAI SHALL use FastAPI as the backend web framework, serving all REST API endpoints.
2. THE KavachAI SHALL use Redis for real-time state management including rate limit counters, session Threat_Scores, active Capability_Tokens, and escalation queue state.
3. THE KavachAI SHALL use SQLite for persistent storage of the Cryptographic_Audit_Trail, policy definitions, agent registrations, and compliance records.
4. WHEN Redis is unavailable, THE KavachAI SHALL fall back to in-memory state management and log a degraded-mode warning, continuing to enforce policies using local state.
5. THE KavachAI SHALL support at least 10 concurrent agent sessions with action evaluation latency under 100 milliseconds per action.
6. THE KavachAI SHALL authenticate all API requests using API key authentication via the X-API-Key header, with API keys stored as salted SHA-256 hashes.
7. THE KavachAI SHALL implement CORS configuration allowing the SOC_Dashboard origin to access all API endpoints.
8. WHEN the KavachAI process starts, THE KavachAI SHALL validate the integrity of the Cryptographic_Audit_Trail by verifying the hash chain for each active session.

[↑ Back to Top](#table-of-contents)

### Requirement 13: Demo Scenario — Multi-Stage Financial Services Attack

**User Story:** As a hackathon presenter, I want a pre-configured demo scenario that showcases a sophisticated multi-stage attack against a financial services AI agent, with KavachAI detecting and neutralizing each stage in real time on the SOC dashboard, so that judges can see the full depth of the system's capabilities.

#### Acceptance Criteria

1. THE KavachAI SHALL include a demo financial services AI agent configured with tools for customer query handling, account lookup, Aadhaar verification, payment processing, email sending, and external API calling.
2. THE demo scenario SHALL simulate a multi-stage attack consisting of: (Stage 1) indirect prompt injection via a crafted customer message containing hidden instructions, (Stage 2) attempted exfiltration of Aadhaar numbers from customer records through the agent's response, (Stage 3) privilege escalation attempt to access admin-level payment processing APIs, (Stage 4) covert data channeling via base64-encoded data embedded in seemingly innocent API call parameters.
3. WHEN the demo agent processes the crafted customer message containing indirect prompt injection, THE Prompt_Injection_Detector SHALL detect the injection attempt, assign a Threat_Score above 0.7, and THE SOC_Dashboard SHALL display the detection as Stage 1 of the Kill_Chain.
4. WHEN the demo agent attempts to include Aadhaar numbers in an outbound response, THE PII_Masker SHALL mask the Aadhaar numbers and THE DPDP_Compliance_Engine SHALL flag a potential data breach, displayed as Stage 2 of the Kill_Chain on the SOC_Dashboard.
5. WHEN the demo agent attempts to invoke the admin payment processing API beyond the agent's Capability_Token scope, THE Privilege_Escalation_Detector SHALL detect the escalation attempt, THE Zero_Trust_Engine SHALL issue a BLOCK verdict, and THE SOC_Dashboard SHALL display the detection as Stage 3 of the Kill_Chain.
6. WHEN the demo agent attempts to embed base64-encoded customer data in API call parameters, THE Covert_Channel_Detector SHALL detect the encoding anomaly, THE Action_Interceptor SHALL issue a QUARANTINE verdict, and THE SOC_Dashboard SHALL display the detection as Stage 4 of the Kill_Chain.
7. WHEN all four attack stages have been detected, THE SOC_Dashboard SHALL display the complete Kill_Chain visualization showing the attack progression, inter-stage dependencies, and the defensive action taken at each stage.
8. THE demo scenario SHALL include a pre-configured KavachAI DSL policy file demonstrating temporal constraints, information flow policies, and DPDP Act compliance rules specific to the financial services context.
9. THE demo scenario SHALL generate an Evidence_Package and an Incident_Report at the conclusion of the attack sequence, demonstrating the law enforcement integration capabilities.
10. THE SOC_Dashboard SHALL display the full demo session timeline, Compliance_Posture, and Kill_Chain_View within 2 seconds of each action completing.
11. THE demo scenario SHALL demonstrate the Ethics_Engine by having the demo agent generate a biased loan recommendation based on regional bias in the customer data, which THE Bias_Detector SHALL detect and flag, and THE SOC_Dashboard SHALL display the ethics violation alongside the security kill chain.

[↑ Back to Top](#table-of-contents)

### Requirement 14: Formal Policy Verification (Dual-Stage)

**User Story:** As a security architect, I want KavachAI policies to be formally verified for correctness before deployment and lightweight-checked at runtime, so that the system provides formal safety guarantees without sacrificing runtime performance — inspired by VeriGuard's dual-stage approach (arXiv:2510.05156).

#### Acceptance Criteria

1. WHEN a policy author submits a new or updated KavachAI DSL policy for deployment, THE Formal_Policy_Verifier SHALL perform offline formal verification before the policy becomes active, checking for: (a) internal consistency (no contradictory rules), (b) completeness (no unhandled action categories within the policy's declared scope), and (c) absence of conflicting enforcement actions for the same trigger-predicate combination.
2. IF the Formal_Policy_Verifier detects a consistency violation (two rules that produce conflicting verdicts for the same Action_Request), THEN THE Formal_Policy_Verifier SHALL reject the policy deployment and return a detailed conflict report identifying the conflicting rules, the overlapping conditions, and a suggested resolution.
3. IF the Formal_Policy_Verifier detects an incompleteness gap (an action category within the policy's declared scope that has no matching rule), THEN THE Formal_Policy_Verifier SHALL issue a warning identifying the uncovered action category and the recommended default verdict.
4. WHEN a policy passes offline formal verification, THE Formal_Policy_Verifier SHALL generate a verification certificate containing the policy hash, verification timestamp, properties proven, and the verifier version.
5. THE Runtime_Policy_Monitor SHALL validate each agent action against pre-verified policies using a lightweight checking mechanism that references the verification certificate rather than re-executing full formal verification at runtime.
6. THE Runtime_Policy_Monitor SHALL add less than 5 milliseconds of overhead per action evaluation beyond the base Policy_Engine evaluation time.
7. WHEN the Runtime_Policy_Monitor detects an action that falls outside the pre-verified policy's coverage (an edge case not covered by offline verification), THE Runtime_Policy_Monitor SHALL escalate the action to the full Policy_Engine for comprehensive evaluation and log the coverage gap for subsequent offline verification.
8. THE Formal_Policy_Verifier SHALL complete offline verification of a policy containing up to 100 rules within 30 seconds. Accessibility note: verification results SHALL be presented in plain language with clear pass/fail indicators and actionable fix suggestions, not raw formal logic output.

[↑ Back to Top](#table-of-contents)

### Requirement 15: DFA-Based Behavioral Modeling

**User Story:** As a safety engineer, I want valid agent workflows encoded as Deterministic Finite Automata so that the runtime engine can verify agent tool-call sequences follow valid paths and detect deviations in real time — inspired by the CORE framework (arXiv:2509.20998).

#### Acceptance Criteria

1. THE KavachAI SHALL support defining DFA_Behavioral_Models that encode valid agent workflows as a set of DFA_States (representing valid agent contexts) and DFA_Transitions (representing valid tool calls between states).
2. WHEN an agent issues an Action_Request, THE Zero_Trust_Engine SHALL check the requested tool call against the agent's current DFA_State to verify that the transition is valid in the agent's DFA_Behavioral_Model.
3. IF an Action_Request would trigger a DFA_Transition that does not exist in the agent's DFA_Behavioral_Model (an invalid state transition), THEN THE Zero_Trust_Engine SHALL issue a BLOCK verdict with an INVALID_STATE_TRANSITION reason and record the violation in the Cryptographic_Audit_Trail.
4. IF an Action_Request would trigger a DFA_Transition into a state explicitly marked as dangerous in the DFA_Behavioral_Model, THEN THE Zero_Trust_Engine SHALL issue an ESCALATE or QUARANTINE verdict based on the danger level configured for that state.
5. THE KavachAI SHALL compute Path_Correctness for each agent session by comparing the agent's actual tool-call sequence against valid paths in the DFA_Behavioral_Model, expressed as the proportion of transitions that follow valid DFA paths.
6. THE KavachAI SHALL compute Harmful_Call_Rate for each agent session as the proportion of tool calls that transition to invalid or dangerous DFA_States.
7. THE KavachAI SHALL compute Prefix_Criticality for each agent session, measuring how early in the action sequence a deviation from valid DFA paths occurs — earlier deviations SHALL result in higher risk scores.
8. THE SOC_Dashboard SHALL display the DFA_Behavioral_Model as an interactive state diagram, highlighting the agent's current state, the path taken, and any invalid transitions attempted.
9. THE KavachAI SHALL support defining DFA_Behavioral_Models via the KavachAI DSL using a workflow definition syntax, and via a visual editor in the SOC_Dashboard for users who prefer graphical workflow design. Accessibility note: the visual DFA editor SHALL provide drag-and-drop state and transition creation, making behavioral modeling accessible without requiring automata theory knowledge.
10. THE Zero_Trust_Engine SHALL evaluate DFA state transitions within 5 milliseconds per action.

[↑ Back to Top](#table-of-contents)

### Requirement 16: Dynamic Trust Scoring

**User Story:** As a platform operator, I want agents to accumulate trust scores based on compliance history so that policy enforcement strictness dynamically adapts to agent behavior — inspired by the Governance-as-a-Service Trust Factor mechanism (arXiv:2508.18765).

#### Acceptance Criteria

1. THE Zero_Trust_Engine SHALL maintain a Trust_Score (0.0 to 1.0) for each registered agent, initialized at 0.5 (STANDARD Trust_Level) upon first registration.
2. WHEN an agent's Action_Request receives an ALLOW verdict, THE Zero_Trust_Engine SHALL increase the agent's Trust_Score by a configurable increment (default 0.01), capped at 1.0.
3. WHEN an agent's Action_Request receives a BLOCK verdict, THE Zero_Trust_Engine SHALL decrease the agent's Trust_Score by a severity-weighted decrement: BLOCK due to policy violation (default -0.05), BLOCK due to threat detection (default -0.10), QUARANTINE (default -0.25).
4. THE Zero_Trust_Engine SHALL classify each agent into a Trust_Level based on Trust_Score: TRUSTED (0.8-1.0), STANDARD (0.5-0.79), RESTRICTED (0.2-0.49), or QUARANTINED (0.0-0.19).
5. WHILE an agent has Trust_Level TRUSTED, THE Policy_Engine SHALL apply a reduced evaluation scope (skip low-priority policy rules) to decrease evaluation latency for consistently compliant agents.
6. WHILE an agent has Trust_Level RESTRICTED, THE Policy_Engine SHALL apply the full policy evaluation scope and additionally require human approval for actions involving sensitive data or high-privilege tools.
7. WHILE an agent has Trust_Level QUARANTINED, THE Zero_Trust_Engine SHALL block all Action_Requests from the agent until a human operator manually reviews and restores the agent's Trust_Level.
8. THE Zero_Trust_Engine SHALL apply Trust_Decay to inactive agents: an agent's Trust_Score SHALL decrease by a configurable rate (default 0.01 per hour of inactivity), with a floor at the STANDARD Trust_Level lower bound (0.5), requiring re-establishment of trust through compliant behavior after extended inactivity.
9. THE Zero_Trust_Engine SHALL implement Graduated_Enforcement based on Trust_Level: warning (logged but not blocked) → throttle (rate-limited) → restrict (human approval required) → quarantine (all actions blocked).
10. THE SOC_Dashboard SHALL display each agent's Trust_Score, Trust_Level, trust history trend, and the factors contributing to trust changes. Accessibility note: trust levels SHALL be displayed with intuitive color coding and plain-language descriptions (e.g., "This agent has a strong compliance track record" for TRUSTED level).
11. THE Cryptographic_Audit_Trail SHALL record all Trust_Score changes with the triggering event, previous score, new score, and the Trust_Level transition (if any).

[↑ Back to Top](#table-of-contents)

### Requirement 17: Determinism Assurance for Regulatory Audit

**User Story:** As a compliance officer in Indian financial services, I want KavachAI to track whether agents produce consistent decisions for identical inputs, so that regulatory auditors can verify agent behavior is reproducible and compliant with DPDP Act requirements — inspired by DFAH research (arXiv:2601.15322).

#### Acceptance Criteria

1. THE Cryptographic_Audit_Trail SHALL record sufficient input context (action parameters, session state snapshot, active policies, agent Trust_Score) for each Audit_Entry to enable deterministic replay of the policy evaluation for that action.
2. WHEN a regulatory auditor initiates an audit replay for a specific agent session, THE KavachAI SHALL re-execute the policy evaluation pipeline for each action in the session using the recorded input context and compare the replayed verdicts against the original verdicts.
3. THE KavachAI SHALL compute Trajectory_Determinism for each audit replay as the proportion of actions where the replayed tool-call sequence matches the original sequence.
4. THE KavachAI SHALL compute Decision_Determinism for each audit replay as the proportion of actions where the replayed Action_Verdict matches the original Action_Verdict.
5. THE KavachAI SHALL generate a Determinism_Report for each audit replay containing: session identifier, Trajectory_Determinism score, Decision_Determinism score, list of non-deterministic actions with detailed divergence analysis, and a compliance assessment.
6. IF the Decision_Determinism score for an audit replay falls below a configurable threshold (default 0.95), THEN THE KavachAI SHALL flag the session as NON_DETERMINISTIC in the Determinism_Report and recommend investigation of the divergent actions.
7. THE SOC_Dashboard SHALL provide an audit replay interface where compliance officers can select a session, initiate replay, and view the Determinism_Report with side-by-side comparison of original and replayed evaluations. Accessibility note: the replay interface SHALL present results in a clear tabular format with color-coded match/mismatch indicators, designed for compliance officers who may not have technical backgrounds.
8. THE KavachAI SHALL support batch audit replay for multiple sessions, generating aggregate determinism statistics suitable for regulatory reporting to Indian financial services authorities under DPDP Act compliance requirements.
9. THE Determinism_Report SHALL be exportable as part of an Evidence_Package for submission to regulatory authorities, with cryptographic signatures ensuring report integrity.

[↑ Back to Top](#table-of-contents)

### Requirement 18: MCP Proxy Gateway Architecture

**User Story:** As a platform operator, I want KavachAI to operate as a transparent MCP proxy gateway that intercepts all tool calls between any MCP-compatible agent and any MCP server, so that safety governance is protocol-native and requires zero code changes in agents or tools.

#### Acceptance Criteria

1. THE MCP_Proxy_Gateway SHALL accept incoming MCP connections from MCP_Clients using the standard MCP transport protocols (stdio and SSE/HTTP).
2. THE MCP_Proxy_Gateway SHALL forward MCP connections to downstream MCP_Servers, maintaining separate sessions per client-server pair.
3. WHEN an MCP_Client sends a tools/call JSON-RPC request, THE MCP_Proxy_Gateway SHALL intercept the request, construct an Action_Request from the tool name and arguments, and submit the Action_Request to the Zero Trust evaluation pipeline before forwarding to the target MCP_Server.
4. WHEN the Zero Trust evaluation pipeline returns an ALLOW verdict for a tools/call request, THE MCP_Proxy_Gateway SHALL forward the original request to the target MCP_Server and relay the response back to the MCP_Client.
5. WHEN the Zero Trust evaluation pipeline returns a BLOCK verdict for a tools/call request, THE MCP_Proxy_Gateway SHALL return a JSON-RPC error response to the MCP_Client containing the Action_Verdict, Reasoning_Trace, and the violated policy rules, WITHOUT forwarding the request to the MCP_Server.
6. WHEN the Zero Trust evaluation pipeline returns an ESCALATE verdict, THE MCP_Proxy_Gateway SHALL hold the request pending human approval via the SOC_Dashboard, and return the tool result or error based on the human decision.
7. WHEN an MCP_Client sends a tools/list request, THE MCP_Proxy_Gateway SHALL forward the request to the target MCP_Server, then filter the response using the Tool_Discovery_Filter to hide tools that the agent's Capability_Token does not authorize.
8. THE MCP_Proxy_Gateway SHALL attach Capability_Labels to tool definitions in the filtered tools/list response, indicating each tool's capability category, confidentiality level, and required trust level.
9. THE MCP_Proxy_Gateway SHALL add less than 50 milliseconds of latency to tool call forwarding under normal operating conditions (excluding evaluation pipeline time).
10. THE MCP_Proxy_Gateway SHALL support proxying to multiple downstream MCP_Servers simultaneously, routing tool calls to the appropriate server based on tool name.
11. THE MCP_Proxy_Gateway SHALL log all intercepted tool calls, forwarded requests, and responses in the Cryptographic_Audit_Trail with full MCP protocol metadata.
12. Accessibility note: configuring the MCP_Proxy_Gateway SHALL require only changing the MCP server URL in the agent's configuration — no agent code changes, no tool server changes. A single configuration line redirects all tool traffic through KavachAI.

[↑ Back to Top](#table-of-contents)

### Requirement 19: MCP Safety Server

**User Story:** As an AI agent developer, I want KavachAI to expose safety tools via MCP so that agents can proactively query their own safety constraints, check policies before acting, and request escalations through the standard MCP protocol.

#### Acceptance Criteria

1. THE MCP_Safety_Server SHALL expose the following tools via the MCP protocol: check_policy (accepts a proposed action and returns the predicted Action_Verdict without executing), get_my_permissions (returns the agent's current Capability_Token scope and Trust_Level), request_escalation (allows the agent to proactively request human review of a planned action), get_compliance_status (returns the agent's current DPDP Act compliance posture), and report_suspicious_input (allows the agent to flag potentially malicious inputs it has received).
2. WHEN an agent calls the check_policy tool, THE MCP_Safety_Server SHALL evaluate the proposed action against all active policies and return the predicted Action_Verdict, matched rules, and Reasoning_Trace WITHOUT recording the check in the Cryptographic_Audit_Trail as an executed action.
3. WHEN an agent calls the get_my_permissions tool, THE MCP_Safety_Server SHALL return the agent's current Capability_Token scope, Trust_Score, Trust_Level, and a human-readable summary of what the agent is and is not authorized to do.
4. WHEN an agent calls the request_escalation tool, THE MCP_Safety_Server SHALL create an escalation request in the Escalation_Manager and return an escalation_id that the agent can reference.
5. WHEN an agent calls the report_suspicious_input tool, THE MCP_Safety_Server SHALL log the reported input in the Cryptographic_Audit_Trail, run the Prompt_Injection_Detector on the input, and return the Threat_Score.
6. THE MCP_Safety_Server SHALL authenticate all tool calls using the agent's Agent_Identity, ensuring that agents can only query their own permissions and compliance status.
7. Accessibility note: the MCP_Safety_Server enables a "safety-aware agent" pattern where agents can be instructed (via system prompt) to check policies before taking risky actions — making safety a collaborative process between the agent and the governance layer.

[↑ Back to Top](#table-of-contents)

### Requirement 20: Deployment and Hosting Infrastructure

**User Story:** As a hackathon presenter, I want KavachAI deployed on cloud infrastructure accessible to external audiences via public URLs, with a local Docker fallback for unreliable network conditions, so that the demo works reliably in any environment.

#### Acceptance Criteria

1. THE KavachAI backend SHALL be deployable to Railway with a single command or GitHub push, using Railway's Python buildpack and Redis addon.
2. THE SOC_Dashboard SHALL be deployable to Vercel as a static React application with environment variables pointing to the Railway-hosted backend API.
3. THE KavachAI SHALL provide a Docker Compose configuration that runs the complete system locally (FastAPI backend, Redis, SQLite, React dashboard) with a single `docker-compose up` command.
4. THE Docker Compose configuration SHALL expose the MCP_Proxy_Gateway on a configurable local port (default 3001), the REST API on port 8000, and the SOC_Dashboard on port 3000.
5. THE KavachAI SHALL provide environment-specific configuration files for: local development, Docker Compose, and cloud deployment (Railway + Vercel).
6. THE cloud deployment SHALL use HTTPS for all endpoints and WebSocket connections.
7. THE KavachAI SHALL include a demo launch script that starts the demo financial services agent, connects it through the MCP_Proxy_Gateway, and triggers the multi-stage attack scenario with a single command.
8. THE demo launch script SHALL work in both cloud-hosted and local Docker modes without configuration changes beyond an environment flag.
9. Accessibility note: the deployment process SHALL be documented with step-by-step instructions suitable for hackathon judges who may want to run the system themselves, including a one-click deploy button for Railway.

[↑ Back to Top](#table-of-contents)

### Requirement 21: Multi-LLM Gateway and LLM-as-a-Service

**User Story:** As a platform operator, I want KavachAI to provide a unified LLM gateway that routes agent requests to multiple model providers with provider-agnostic safety governance, cost tracking, and intelligent fallback, so that agents can use the best model for each task while maintaining consistent safety standards.

#### Acceptance Criteria

1. THE LLM_Gateway SHALL provide a unified API endpoint that accepts LLM completion requests and routes them to configured model providers (OpenAI, Anthropic, Google, and open-source models via Ollama or vLLM).
2. THE LLM_Gateway SHALL maintain Model_Profiles for each configured LLM model, specifying the model's risk level (low/medium/high), capability tier, cost per token, maximum context window, and model-specific safety constraints.
3. WHEN an agent sends an LLM completion request, THE LLM_Request_Interceptor SHALL scan the prompt for prompt injection attempts, sensitive data leakage, and policy violations BEFORE forwarding the request to the LLM provider.
4. WHEN an LLM provider returns a completion response, THE LLM_Request_Interceptor SHALL scan the response for toxic content, biased outputs, hallucinated claims, and policy violations BEFORE returning the response to the agent.
5. THE LLM_Gateway SHALL support Model_Fallback_Chains: if the primary model provider returns an error or is unavailable, THE LLM_Gateway SHALL automatically route the request to the next model in the fallback chain.
6. THE LLM_Gateway SHALL enforce LLM_Budget limits per agent, per session, and per organization, tracking token usage and estimated cost across all model providers.
7. WHEN an agent's LLM_Budget is exhausted, THE LLM_Gateway SHALL block further LLM requests from that agent and notify the SOC_Dashboard.
8. THE LLM_Gateway SHALL support intelligent model routing based on task type: routing simple queries to cost-effective models and complex reasoning tasks to more capable models, based on configurable routing rules.
9. THE LLM_Gateway SHALL log all LLM requests and responses (with configurable redaction of sensitive content) in the Cryptographic_Audit_Trail, including model used, token count, latency, and cost.
10. THE LLM_Gateway SHALL support configuring model-specific safety constraints: for example, requiring human approval for requests to high-capability models that exceed a token threshold.
11. Accessibility note: the LLM_Gateway SHALL provide a dashboard view in the SOC_Dashboard showing real-time LLM usage statistics, cost breakdown by model/agent/session, and model availability status.

[↑ Back to Top](#table-of-contents)

### Requirement 22: AI Ethics and Responsible AI Guardrails

**User Story:** As a responsible AI practitioner, I want KavachAI to enforce comprehensive AI ethics guardrails covering bias detection, toxicity filtering, fairness monitoring, and content safety, so that AI agents operate within ethical boundaries aligned with India's AI Governance Guidelines and global responsible AI standards.

#### Acceptance Criteria

1. THE Ethics_Engine SHALL evaluate every agent output against four ethical dimensions: bias (discriminatory content), toxicity (harmful/offensive content), fairness (systematic discrimination patterns), and content safety (illegal/dangerous content).
2. THE Bias_Detector SHALL detect biased content across India-specific categories: gender bias, caste-based discrimination, religious bias, regional/linguistic bias, and socioeconomic bias, using configurable sensitivity thresholds.
3. THE Toxicity_Filter SHALL classify agent inputs and outputs against toxicity categories (hate speech, harassment, threats, self-harm, sexual content, violence) and assign a toxicity score (0.0 to 1.0).
4. WHEN the Toxicity_Filter assigns a toxicity score above a configurable threshold (default 0.7) to an agent output, THE Ethics_Engine SHALL block the output and return a sanitized alternative or an error message to the agent.
5. THE Fairness_Monitor SHALL track agent behavior patterns across interactions within a session and across sessions, detecting systematic unfairness such as consistently different treatment based on user demographics inferred from context.
6. WHEN the Fairness_Monitor detects a statistically significant fairness violation (p-value below configurable threshold, default 0.05), THE Fairness_Monitor SHALL flag the agent session and generate a fairness alert on the SOC_Dashboard.
7. THE Content_Safety_Classifier SHALL classify agent outputs against configurable content safety categories and block outputs that fall into prohibited categories, with the category list configurable per deployment context (e.g., financial services, healthcare, government).
8. THE Ethics_Engine SHALL compute an Ethics_Score for each agent session by aggregating bias, toxicity, fairness, and content safety assessments, and display the Ethics_Score on the SOC_Dashboard alongside the Threat_Score and Trust_Score.
9. THE Ethics_Engine SHALL support configurable ethics policies expressed in the KavachAI DSL, allowing organizations to define their own ethical boundaries (e.g., "ALWAYS agent output must not contain caste-based references when processing loan applications").
10. THE Cryptographic_Audit_Trail SHALL record all ethics evaluations, including the Ethics_Score, detected violations, and the specific ethical dimension violated, for each agent action that produces output.
11. Accessibility note: ethics violations SHALL be displayed on the SOC_Dashboard with clear, non-technical explanations of what was detected and why it was flagged, suitable for compliance officers and ethics review boards.

[↑ Back to Top](#table-of-contents)

### Requirement 23: Hallucination Detection and Output Grounding

**User Story:** As a safety engineer, I want KavachAI to detect when agents hallucinate tool results, fabricate data, or present unverified claims as facts, so that end users receive only grounded, verified information — inspired by tool receipts research (arXiv:2603.10060).

#### Acceptance Criteria

1. THE Hallucination_Detector SHALL compare agent claims about tool execution results against the actual Action_Attestation records in the Cryptographic_Audit_Trail to detect fabricated tool executions.
2. WHEN an agent claims to have executed a tool that has no corresponding Action_Attestation in the Cryptographic_Audit_Trail for the current session, THE Hallucination_Detector SHALL flag the claim as a TOOL_FABRICATION hallucination.
3. WHEN an agent reports tool output values that differ from the actual tool response recorded in the Cryptographic_Audit_Trail, THE Hallucination_Detector SHALL flag the discrepancy as a RESULT_MISSTATEMENT hallucination.
4. THE Hallucination_Detector SHALL detect when an agent presents inferences or reasoning as verified facts by comparing agent output claims against the grounding data available in the session's tool responses.
5. THE Output_Validator SHALL validate agent final outputs (responses to users, reports, summaries) against the session's tool response data, flagging claims that cannot be traced to any tool response as UNGROUNDED.
6. WHEN the Hallucination_Detector detects a hallucination, THE Hallucination_Detector SHALL assign a hallucination severity (LOW: minor misstatement, MEDIUM: significant fabrication, HIGH: complete tool fabrication) and record the detection in the Cryptographic_Audit_Trail.
7. WHEN a HIGH severity hallucination is detected, THE Hallucination_Detector SHALL block the agent output and escalate to the SOC_Dashboard for human review.
8. THE SOC_Dashboard SHALL display a grounding verification view for each agent session, showing which agent claims are grounded in tool responses (green), partially grounded (yellow), or ungrounded (red).
9. Accessibility note: the grounding verification view SHALL present results in a simple claim-by-claim format with clear source attribution, making it easy for non-technical reviewers to verify agent output accuracy.

[↑ Back to Top](#table-of-contents)

### Requirement 24: India AI Governance Guidelines Compliance

**User Story:** As a government compliance officer, I want KavachAI to map its capabilities to India's AI Governance Guidelines 2025 ("Seven Sutras") and generate compliance reports, so that organizations can demonstrate alignment with India's national AI governance framework.

#### Acceptance Criteria

1. THE India_AI_Governance_Mapper SHALL map KavachAI's capabilities to each of the seven principles of India's AI Governance Guidelines 2025: (1) Trust — mapped to Cryptographic_Audit_Trail, Action_Attestation, and Determinism Assurance; (2) People First — mapped to Human-in-the-Loop Escalation and Escalation_Manager; (3) Innovation over Restraint — mapped to Dynamic Trust Scoring and Graduated_Enforcement; (4) Fairness & Equity — mapped to Ethics_Engine, Bias_Detector, and Fairness_Monitor; (5) Accountability — mapped to Chain_of_Custody, Evidence_Package, and CERT_In_Reporter; (6) Understandable by Design — mapped to Reasoning_Traces, SOC_Dashboard, and DSL accessibility features; (7) Safety, Resilience & Sustainability — mapped to Zero_Trust_Engine, Threat_Detector, and DFA_Behavioral_Model.
2. THE India_AI_Governance_Mapper SHALL generate a Seven_Sutras_Compliance report for each agent session or deployment, scoring compliance on each of the seven principles on a scale of 0-100%.
3. THE SOC_Dashboard SHALL display a Seven Sutras compliance radar chart showing the organization's alignment with each of the seven principles across all active agent sessions.
4. THE Seven_Sutras_Compliance report SHALL include specific evidence from the Cryptographic_Audit_Trail demonstrating compliance with each principle (e.g., for "People First": count of human escalations, human override rate, average escalation response time).
5. THE Seven_Sutras_Compliance report SHALL be exportable as a PDF document suitable for submission to MeitY or other regulatory bodies.
6. THE KavachAI DSL SHALL support ethics-specific policy constructs that map directly to the Seven Sutras (e.g., "ENSURE fairness IN loan_processing FOR ALL demographic_groups" maps to Fairness & Equity).
7. Accessibility note: the Seven Sutras compliance report SHALL use plain language and visual indicators (radar charts, progress bars, color coding) to make governance compliance understandable to non-technical stakeholders including government officials and policy makers.

[↑ Back to Top](#table-of-contents)

### Requirement 25: LLM Cost and Usage Governance

**User Story:** As a platform operator, I want KavachAI to enforce cost controls and usage governance for LLM API consumption, so that runaway agents cannot exhaust API budgets and usage is tracked for billing and optimization.

#### Acceptance Criteria

1. THE LLM_Gateway SHALL track token usage (input tokens, output tokens, total tokens) and estimated cost for every LLM request, broken down by model, agent, session, and organization.
2. THE LLM_Gateway SHALL enforce configurable LLM_Budget limits at three levels: per-agent (maximum spend per agent lifetime), per-session (maximum spend per session), and per-organization (maximum spend per billing period).
3. WHEN an LLM request would cause the agent's cumulative cost to exceed the per-agent LLM_Budget, THE LLM_Gateway SHALL block the request and return a BUDGET_EXCEEDED error to the agent.
4. WHEN an organization's cumulative LLM cost reaches 80% of the per-organization LLM_Budget, THE LLM_Gateway SHALL send a budget warning alert to the SOC_Dashboard.
5. THE LLM_Gateway SHALL support configurable cost-optimization rules: for example, automatically downgrading to a cheaper model when the session budget is 50% consumed and the task complexity is below a configurable threshold.
6. THE SOC_Dashboard SHALL display a real-time cost dashboard showing LLM spending by model, agent, session, and time period, with trend charts and budget utilization gauges.
7. THE Cryptographic_Audit_Trail SHALL record the LLM cost for each action that involved an LLM request, enabling cost attribution in Evidence_Packages and audit reports.
8. Accessibility note: the cost dashboard SHALL present spending data in clear, business-friendly formats (currency amounts, percentage of budget used, projected monthly spend) suitable for finance teams and management.

[↑ Back to Top](#table-of-contents)

### Requirement 26: LLM Explainability and Decision Transparency

**User Story:** As an AI policy maker, I want every agent decision to be explainable at multiple levels — the LLM's own reasoning, the policy evaluation, and a plain-language summary — so that decisions can be understood, audited, and challenged by all stakeholders including affected individuals.

#### Acceptance Criteria

1. WHEN an agent makes a decision that results in a tool call, THE LLM_Reasoning_Capture SHALL record the full chain-of-thought reasoning from the LLM, including the prompt context, the model's intermediate reasoning steps, and the final action decision, in the Cryptographic_Audit_Trail.
2. THE KavachAI SHALL generate a Decision_Explanation for every agent action containing three layers: (a) LLM Reasoning Layer — the model's chain-of-thought explaining why it chose this action, (b) Policy Layer — the KavachAI policy evaluation result explaining why the action was allowed, blocked, or escalated, and (c) User-Facing Layer — a plain-language summary suitable for non-technical stakeholders.
3. WHEN a human operator views an action in the SOC_Dashboard, THE SOC_Dashboard SHALL display all three layers of the Decision_Explanation, with the ability to expand/collapse each layer.
4. THE User_Facing_Explanation SHALL be generated in configurable languages (default: English and Hindi) to support India's multilingual context.
5. THE KavachAI SHALL support configurable Explanation_Templates for different audiences: (a) "technical" template for security analysts (includes full reasoning chain, policy rule IDs, threat scores), (b) "compliance" template for auditors (includes policy justification, regulatory mapping, evidence references), (c) "individual" template for affected persons (includes plain-language reason, what data was used, how to challenge the decision), (d) "executive" template for management (includes risk summary, compliance status, business impact).
6. WHEN an affected individual requests an explanation of an agent decision under the right to explanation (DPDP Act Section 11 or EU AI Act Article 86), THE KavachAI SHALL generate a User_Facing_Explanation from the stored Decision_Explanation within 5 seconds.
7. THE LLM_Reasoning_Capture SHALL enforce that agents using the LLM_Gateway include chain-of-thought reasoning in their LLM requests (by injecting a reasoning instruction into the system prompt if not already present), ensuring that reasoning is always available for capture.
8. THE Cryptographic_Audit_Trail SHALL store the LLM_Reasoning_Capture as part of each Audit_Entry, cryptographically linked to the action it explains, ensuring that explanations cannot be retroactively altered.
9. Accessibility note: the User_Facing_Explanation SHALL use plain language at a reading level accessible to the general public (target: 8th grade reading level), avoid technical jargon, and include a clear statement of what the individual can do if they disagree with the decision (e.g., contact information for human review).

[↑ Back to Top](#table-of-contents)

### Requirement 27: Model Transparency and Provenance

**User Story:** As a regulatory auditor, I want full transparency into which LLM models are being used, their known limitations, and their provenance, so that I can assess whether the models are appropriate for the decisions being made.

#### Acceptance Criteria

1. THE LLM_Gateway SHALL maintain a Model_Card for each configured LLM model, containing: model name, version, provider, model family, parameter count (if known), known limitations, bias evaluation summary, training data provenance summary (as disclosed by the provider), performance benchmarks on relevant tasks, and the date of last evaluation.
2. THE Cryptographic_Audit_Trail SHALL record a Model_Provenance_Record for every action that involved an LLM request, containing: the model name and version used, the provider, the temperature and other generation parameters, the token count (input/output), and the latency.
3. THE SOC_Dashboard SHALL provide a Model Registry view displaying all configured LLM models with their Model_Cards, current usage statistics, and performance metrics.
4. WHEN a regulatory auditor requests model information for a specific agent session, THE KavachAI SHALL generate a Model Transparency Report containing: all models used during the session, the Model_Card for each model, the number of requests per model, and any model-specific safety incidents detected.
5. THE Model_Card SHALL include a "Suitability Assessment" section where the deploying organization documents why this model is appropriate for the specific use case (e.g., "GPT-4 is used for customer query classification because it scored 92% accuracy on our financial services benchmark").
6. THE LLM_Gateway SHALL flag when an agent uses a model that has known limitations relevant to the current task (e.g., using a model with known bias in financial decisions for a loan processing task) and record the flag in the Cryptographic_Audit_Trail.
7. THE Model Transparency Report SHALL be exportable as part of an Evidence_Package, with cryptographic signatures ensuring integrity.
8. Accessibility note: Model_Cards SHALL be displayed in a structured, readable format on the SOC_Dashboard with clear sections for limitations and bias information, making it easy for non-ML-experts to understand model characteristics.

[↑ Back to Top](#table-of-contents)

### Requirement 28: LLM Observability and Performance Monitoring

**User Story:** As an enterprise architect, I want real-time observability into LLM performance across all models in the gateway, so that I can detect degradation, drift, and anomalies before they impact agent behavior.

#### Acceptance Criteria

1. THE LLM_Observability component SHALL track the following metrics for each LLM model in real-time: response latency (p50, p95, p99), error rate, token throughput, refusal rate (model declines to respond), and response quality score (based on configurable quality heuristics).
2. THE Model_Drift_Detector SHALL establish baseline performance metrics for each model during an initial calibration period (configurable, default: first 100 requests) and continuously compare current performance against the baseline.
3. WHEN the Model_Drift_Detector detects that a model's refusal rate has increased by more than 2x compared to baseline, OR response latency p95 has increased by more than 3x, OR error rate has increased by more than 5x, THE Model_Drift_Detector SHALL generate a MODEL_DRIFT alert on the SOC_Dashboard.
4. WHEN a MODEL_DRIFT alert is generated, THE LLM_Gateway SHALL optionally (if configured) automatically route new requests to the next model in the Model_Fallback_Chain until the drift is resolved.
5. THE SOC_Dashboard SHALL provide an LLM Observability panel displaying real-time performance metrics for all models, with time-series charts, anomaly highlights, and model comparison views.
6. THE LLM_Observability component SHALL track response quality by comparing LLM outputs against expected patterns for the task type (e.g., for classification tasks: checking that outputs match expected label formats; for generation tasks: checking output length and coherence heuristics).
7. THE Cryptographic_Audit_Trail SHALL record LLM performance metrics (latency, token count, model version) for each LLM request, enabling historical performance analysis in Evidence_Packages.
8. Accessibility note: the LLM Observability panel SHALL use traffic-light indicators (green/yellow/red) for model health status, making it immediately clear to operations teams which models need attention.

[↑ Back to Top](#table-of-contents)

### Requirement 29: Multi-Tenant Enterprise Deployment

**User Story:** As an enterprise architect deploying KavachAI across multiple business units, I want strict tenant isolation so that each business unit has its own policies, agents, budgets, and audit trails without cross-tenant data leakage.

#### Acceptance Criteria

1. THE KavachAI SHALL support multi-tenant deployment where each Tenant has isolated: KavachAI DSL policies, agent registrations and Capability_Tokens, Cryptographic_Audit_Trail entries, LLM_Budget allocations, Ethics_Engine configurations, and DPDP compliance settings.
2. THE Tenant_Isolation boundary SHALL ensure that API requests authenticated with one Tenant's API key cannot access agents, sessions, audit data, or policies belonging to another Tenant.
3. THE KavachAI SHALL support Tenant-level LLM_Gateway configuration, allowing each Tenant to configure its own set of LLM models, Model_Fallback_Chains, and model-specific safety constraints.
4. THE SOC_Dashboard SHALL support Tenant-scoped views, where a Tenant administrator sees only their own agents, sessions, policies, and compliance data.
5. THE KavachAI SHALL support a super-admin role that can view cross-Tenant aggregate metrics (total actions, total violations, system health) without accessing individual Tenant data.
6. THE Cryptographic_Audit_Trail SHALL include the Tenant identifier in each Audit_Entry, and queries SHALL be automatically scoped to the requesting Tenant's data.
7. THE KavachAI SHALL enforce Tenant-level rate limits to prevent one Tenant's workload from degrading performance for other Tenants.
8. Accessibility note: Tenant onboarding SHALL be achievable through a self-service wizard in the SOC_Dashboard that guides administrators through policy configuration, agent registration, and LLM setup with step-by-step instructions.

[↑ Back to Top](#table-of-contents)

### Requirement 30: LLM Evaluation and Continuous Safety Benchmarking

**User Story:** As a head of engineering, I want every LLM model to be systematically evaluated against safety, accuracy, and domain-specific benchmarks before it is allowed in the gateway, and continuously monitored during operation, so that only models meeting our safety standards are used for agent decisions.

#### Acceptance Criteria

1. THE LLM_Eval_Engine SHALL support configurable Safety_Benchmarks containing test suites for: prompt injection resistance, toxicity generation rate, bias across protected categories, hallucination rate, instruction following accuracy, and domain-specific correctness (e.g., financial regulations, healthcare protocols).
2. BEFORE a new LLM model is added to the LLM_Gateway, THE LLM_Eval_Engine SHALL execute the configured Safety_Benchmarks against the model and compute a Model_Safety_Score.
3. IF a model's Model_Safety_Score falls below a configurable threshold (default: 70/100), THE LLM_Eval_Engine SHALL block the model from being added to the LLM_Gateway and generate a detailed evaluation report identifying the failing categories.
4. THE Red_Team_Runner SHALL automatically generate adversarial test cases (prompt injections, jailbreak attempts, bias-triggering prompts) and execute them against each model in the LLM_Gateway on a configurable schedule (default: weekly).
5. WHEN the Red_Team_Runner detects that a model's safety performance has degraded below the threshold since the last evaluation, THE LLM_Eval_Engine SHALL generate a SAFETY_DEGRADATION alert on the SOC_Dashboard and optionally remove the model from active routing.
6. THE LLM_Eval_Engine SHALL support head-to-head model comparison, displaying side-by-side safety scores, benchmark results, and cost-effectiveness metrics on the SOC_Dashboard.
7. THE LLM_Eval_Engine SHALL maintain a historical record of all model evaluations in the Cryptographic_Audit_Trail, enabling auditors to verify that models were properly evaluated before deployment.
8. THE SOC_Dashboard SHALL display a Model Evaluation dashboard showing each model's current Model_Safety_Score, historical score trends, benchmark breakdowns, and the date of last evaluation.
9. Accessibility note: evaluation reports SHALL present results in clear pass/fail format with plain-language explanations of what each benchmark tests and why the model passed or failed, suitable for non-ML stakeholders approving model deployments.

[↑ Back to Top](#table-of-contents)

### Requirement 31: Semantic Grounding Layer

**User Story:** As an enterprise architect, I want a deterministic semantic grounding layer that validates agent decisions and outputs against verified knowledge sources — knowledge graphs, domain ontologies, and structured schemas — so that agent outputs are grounded in facts rather than relying solely on LLM parametric knowledge, significantly reducing hallucinations.

#### Acceptance Criteria

1. THE Semantic_Grounding_Layer SHALL maintain configurable Knowledge_Graphs containing domain-specific entities, relationships, and verified facts that agents can query and that are used to validate agent output claims.
2. THE Semantic_Grounding_Layer SHALL maintain configurable Domain_Ontologies that define the valid concepts, properties, and relationships within each deployment domain (e.g., for financial services: account types, transaction categories, regulatory requirements, valid Aadhaar formats).
3. THE Schema_Enforcer SHALL validate every structured agent output against predefined JSON schemas before the output is returned to the user, rejecting outputs that do not conform to the expected schema and returning a schema violation error to the agent.
4. WHEN an agent produces an output containing factual claims (e.g., "the customer's account balance is ₹50,000"), THE Semantic_Grounding_Layer SHALL verify the claim against the Knowledge_Graph and tool response data, computing a Grounding_Score for the output.
5. WHEN an agent output has a Grounding_Score below a configurable threshold (default: 0.7), THE Semantic_Grounding_Layer SHALL flag the output as INSUFFICIENTLY_GROUNDED and either block the output (strict mode) or attach a grounding warning (advisory mode).
6. THE Semantic_Grounding_Layer SHALL generate Source_Attribution for each claim in an agent's output, linking the claim to the specific knowledge source (knowledge graph node, retrieved document, tool response) that supports it.
7. THE Deterministic_Validator SHALL perform the following non-LLM validations on agent outputs: (a) numerical consistency checks (e.g., totals match line items), (b) date/time validity checks, (c) entity existence verification against the Knowledge_Graph, (d) regulatory constraint checks against the Domain_Ontology (e.g., loan amount within permitted range), and (e) cross-reference validation between tool responses and agent claims.
8. THE Semantic_Grounding_Layer SHALL be positioned in the evaluation pipeline AFTER the LLM generates its response and BEFORE the response is returned to the user, acting as a deterministic "fact-check" gate.
9. THE SOC_Dashboard SHALL display a Grounding Report for each agent session showing the Grounding_Score, Source_Attributions, and any claims flagged as ungrounded, with the ability to drill down into the knowledge sources used for verification.
10. THE Semantic_Grounding_Layer SHALL support loading Knowledge_Graphs and Domain_Ontologies from configurable sources: local JSON/YAML files, external graph databases (Neo4j), or API endpoints — enabling integration with existing enterprise knowledge management systems.
11. Accessibility note: the Grounding Report SHALL present source attributions in a simple "claim → source" format, making it immediately clear to non-technical reviewers which agent statements are backed by verified data and which are not.

[↑ Back to Top](#table-of-contents)

## Technology Stack Rationale and Deployment Model

### Technology Stack Rationale

| Technology | Choice | Rationale |
|---|---|---|
| Backend Framework | Python 3.11+ / FastAPI | Async-native for concurrent agent sessions, auto-generated OpenAPI docs for hackathon demo, rich AI/ML ecosystem (LangChain, MCP SDK, cryptography libraries all Python-native). FastAPI's sub-100ms response times meet pipeline latency requirements. |
| Database | SQLite | Zero-configuration, single-file deployment ideal for hackathon portability. Hash chain integrity verification is straightforward with sequential writes. No external database server needed. Sufficient for 10+ concurrent sessions. |
| Cache / Real-time State | Redis | Pub/sub for real-time WebSocket dashboard updates, sorted sets for escalation priority queues, atomic counters for rate limiting and budget tracking, TTL-based key expiry for session management. |
| DSL Parser | PEG (Python `lark` library) | Composable grammars with excellent error messages, Python-native, supports the trigger-predicate-enforcement pattern and LTL operators. Lark provides Earley and LALR parsing with automatic AST construction. |
| Cryptography | Ed25519 (PyNaCl) + SHA-256 | Ed25519 for fast agent identity signing/verification (compact 32-byte keys, ~10,000 signatures/sec). SHA-256 for hash chain integrity (industry standard, hardware-accelerated on modern CPUs). |
| Frontend | React 18 + Next.js + TailwindCSS | Next.js for SSR initial load performance, React for rich interactive dashboard components, TailwindCSS for rapid UI development. Recharts for standard charts, D3.js for kill chain graph and DFA state diagram visualizations. |
| MCP Integration | `mcp` Python SDK | Official MCP SDK for both proxy gateway and safety server implementation. Supports stdio and SSE transports. |
| LLM Providers | LiteLLM / direct provider SDKs | LiteLLM provides a unified interface to 100+ LLM providers with a single API. Fallback to direct SDKs (openai, anthropic, google-generativeai) for provider-specific features. |
| Containerization | Docker + Docker Compose | Ensures reproducible deployment across hackathon environments. Single `docker-compose up` for complete system. |

### Deployment Model

KavachAI uses a hybrid cloud + local deployment model:

1. **Primary: Cloud-hosted (Railway + Vercel)** — The backend (FastAPI + Redis) deploys to Railway with a single GitHub push. The SOC Dashboard deploys to Vercel as a static React app. Both are accessible via public HTTPS URLs, enabling judges and external audiences to interact with the live system from any device. Railway provides managed Redis as an addon, persistent volumes for SQLite, and automatic HTTPS.

2. **Fallback: Local Docker** — A complete Docker Compose configuration runs the entire system locally. This is critical for hackathon reliability — WiFi at venues can be unreliable. The demo launch script works identically in both modes with a single environment flag toggle.

3. **Why not AWS/GCP/Azure?** — For a hackathon demo, managed cloud platforms add unnecessary complexity (IAM, VPC, security groups) without proportional benefit. Railway and Vercel provide the same reliability with zero infrastructure management. The architecture is cloud-agnostic — migrating to AWS (ECS + ElastiCache + RDS) or GCP (Cloud Run + Memorystore) requires only configuration changes, not code changes.

4. **Data Sovereignty** — All data (audit trails, knowledge graphs, policies) is stored in SQLite on the deployment host. No data leaves the deployment boundary unless explicitly configured. This aligns with DPDP Act data localization requirements.

[↑ Back to Top](#table-of-contents)

## References and Acknowledgments

### Academic Research (arXiv)

1. AgentSpec — Customizable Runtime Enforcement DSL — https://arxiv.org/abs/2503.18666
2. VeriGuard — Dual-Stage Formal Verification — https://arxiv.org/abs/2510.05156
3. Temporal Logic for Agent Correctness — https://arxiv.org/abs/2509.20364
4. CORE Framework — DFA-Based Agent Evaluation — https://arxiv.org/abs/2509.20998
5. DFAH — Determinism-Faithfulness Assurance Harness — https://arxiv.org/abs/2601.15322
6. ShieldAgent — Verifiable Safety Policy Reasoning — https://arxiv.org/abs/2503.22738
7. STAC — Sequential Tool Attack Chaining — https://arxiv.org/abs/2509.25624
8. Governance-as-a-Service — https://arxiv.org/abs/2508.18765
9. Fusion of LLMs and Formal Methods — https://arxiv.org/abs/2412.06512
10. Capability-Enhanced MCP Framework — https://arxiv.org/abs/2601.08012
11. MCPShield — Security Cognition Layer — https://arxiv.org/abs/2602.14281
12. Tool Receipts for Hallucination Detection — https://arxiv.org/abs/2603.10060
13. Comprehensive LLM Guardrails Taxonomy — https://arxiv.org/abs/2406.12934
14. Explainability in Agentic AI Systems — https://arxiv.org/abs/2601.17168
15. LLM-Driven Explainable AI Pipelines — https://arxiv.org/abs/2511.07086
16. OpenAgentSafety — Comprehensive Agent Safety Evaluation — https://arxiv.org/abs/2507.06134
17. Neuro-Symbolic Framework for Safe Agentic AI — https://arxiv.org/abs/2512.20275
18. MAS-Shield (formerly AgentShield) — Defense Framework for LLM MAS — https://arxiv.org/abs/2511.22924

### Industry Research

19. McKinsey — "Deploying Agentic AI with Safety and Security: A Playbook for Technology Leaders" (October 2025) — https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/deploying-agentic-ai-with-safety-and-security-a-playbook-for-technology-leaders
20. McKinsey — "Trust in the Age of Agents" (March 2026) — https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/trust-in-the-age-of-agents

### Regulatory Frameworks

21. India AI Governance Guidelines (MeitY, November 2025) — https://www.meity.gov.in
22. Digital Personal Data Protection Act 2023 (DPDP Act) — https://www.meity.gov.in/data-protection-framework
23. NIST AI Risk Management Framework (AI RMF 1.0) — https://airc.nist.gov/AI_RMF_Interactivity
24. EU AI Act (Regulation 2024/1689) — https://eur-lex.europa.eu/eli/reg/2024/1689

### Protocol Standards

25. Model Context Protocol (MCP) — https://modelcontextprotocol.io

### Acknowledgments

KavachAI acknowledges the foundational contributions of the research community whose work directly informs this system's architecture. The project name 'Kavach' (कवच) draws from the Sanskrit word meaning 'armor' or 'protective shield', reflecting the system's role as a protective governance layer for autonomous AI agents. This project was developed for the ISB Hackathon on Cybersecurity & AI Safety 2025-26, organized by the Indian School of Business (ISB Mohali), Punjab Police State Cyber Crime Division, and CyberPeace Foundation.

[↑ Back to Top](#table-of-contents)