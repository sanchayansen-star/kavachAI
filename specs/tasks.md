# Implementation Plan: KavachAI — Zero Trust Safety Firewall for Agentic AI

## Overview

This plan is ordered for maximum hackathon demo impact. The core pipeline (identity → policy → threat → audit) is built first, followed by the demo scenario, then the dashboard, then advanced features. Each task builds incrementally so the system is demoable as early as possible.

## Tasks

- [ ] 1. Project scaffolding and data models
  - [ ] 1.1 Create project structure and configuration
    - Create `kavachai/backend/` directory tree matching design Section 15
    - Create `main.py` FastAPI entry point with CORS, lifespan, and router includes
    - Create `config.py` with environment-specific settings (local, docker, cloud)
    - Create `requirements.txt` with all dependencies (fastapi, uvicorn, pynacl, lark, redis, litellm, mcp)
    - Create `.env.example` with all required environment variables
    - _Requirements: 12.1, 12.2, 12.3, 20.5_

  - [ ] 1.2 Implement core Pydantic data models
    - Create `models/agent.py`: AgentIdentity, CapabilityToken, ToolScope, TrustLevel enum
    - Create `models/action.py`: ActionRequest, ActionVerdict, VerdictType enum, ActionAttestation
    - Create `models/audit.py`: AuditEntry, EvidencePackage
    - Create `models/threat.py`: KillChain, KillChainStage
    - Create `models/policy.py`: PolicyAST, VerificationCertificate
    - Create `models/grounding.py`: GroundingResult, ClaimVerification, SourceAttribution, ValidationCheck
    - Create `models/evaluation.py`: ModelSafetyScore, SafetyBenchmark, TestSuite, RedTeamResult
    - _Requirements: 1.1, 1.4, 3.7, 5.4, 6.1, 31.4_

  - [ ]* 1.3 Write property tests for data models
    - **Property 4: Trust Score Bounds** — verify trust_score stays in [0.0, 1.0] and trust_level matches defined ranges for any sequence of updates
    - **Validates: Requirements 16.1, 16.4**

  - [ ] 1.4 Set up database layer
    - Create `db/database.py`: SQLite connection manager, schema initialization from design Section 6
    - Create all tables: audit_entries, agents, capability_tokens, policies, dfa_models, kill_chains, escalations, model_evaluations, knowledge_graphs, domain_ontologies, grounding_results, tenants
    - Create `db/redis_client.py`: Redis connection helper with all key patterns from design Section 7
    - _Requirements: 6.1, 12.4, 12.5_

- [ ] 2. Agent identity and cryptographic core
  - [ ] 2.1 Implement Agent Identity Manager
    - Create `core/identity.py`: AgentIdentityManager with Ed25519 key pair generation (PyNaCl)
    - Implement agent registration (issue agent_id, key pair, capability scope, default trust level)
    - Implement capability token issuance with scoped tools, parameter constraints, expiry, and Ed25519 signature
    - Implement signature verification for ActionRequests
    - Implement agent and token revocation
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8_

  - [ ]* 2.2 Write property test for capability token scope enforcement
    - **Property 11: Capability Token Scope Enforcement** — an agent can never invoke a tool not in its active CapabilityToken; out-of-scope calls always produce BLOCK with PRIVILEGE_VIOLATION
    - **Validates: Requirements 1.4, 1.5**

  - [ ] 2.3 Implement API routes for agent management
    - Create `api/routes_eval.py`: POST /api/v1/agents/register, PUT /api/v1/agents/{agent_id}/capabilities, DELETE /api/v1/agents/{agent_id}
    - Implement X-API-Key authentication middleware
    - _Requirements: 1.1, 1.4, 1.6, 11.1_

- [ ] 3. Checkpoint — Agent identity and crypto working
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. KavachAI DSL parser and policy engine
  - [ ] 4.1 Implement DSL parser with Lark
    - Create `core/dsl_parser.py`: PEG grammar from design Section 5 using Lark
    - Parse policy headers, imports, rule blocks (trigger-predicate-enforcement)
    - Support tool_call triggers, comparison/logical predicates, enforcement actions (allow/block/flag/escalate/quarantine)
    - Support temporal triggers (within duration), LTL operators (always/eventually/until/next)
    - Support workflow/DFA definitions (states, transitions, guards)
    - Support parameterized templates and ethics constructs
    - Return structured PolicyAST with line/column error reporting on syntax errors
    - _Requirements: 2.1, 2.2, 2.8, 2.11, 2.12, 2.16_

  - [ ] 4.2 Implement DSL pretty printer
    - Create `core/dsl_printer.py`: serialize PolicyAST back to valid KavachAI DSL source text
    - _Requirements: 2.6, 2.7_

  - [ ]* 4.3 Write property test for DSL round-trip
    - **Property 1: DSL Round-Trip** — parse(print(parse(source))) == parse(source) for valid DSL programs
    - **Validates: Requirements 2.7**

  - [ ] 4.4 Implement policy engine
    - Create `core/policy_engine.py`: PolicyEngine that loads compiled ASTs and evaluates ActionRequests
    - Implement trigger matching (tool_call patterns, state triggers, temporal triggers)
    - Implement predicate evaluation (comparisons, logical expressions, temporal predicates, flow predicates)
    - Implement enforcement action mapping to VerdictType
    - Track action timestamps per session for temporal constraint enforcement
    - Target: single rule evaluation within 10ms
    - _Requirements: 2.3, 2.4, 2.10, 2.11, 2.13, 2.14, 2.15_

  - [ ] 4.5 Implement policy management API routes
    - Create `api/routes_policy.py`: PUT /api/v1/policies, GET /api/v1/policies, GET /api/v1/policies/{policy_id}
    - Parse DSL on upload, store AST in SQLite, support hot reload
    - _Requirements: 2.5, 2.9_

- [ ] 5. Threat detection engine
  - [ ] 5.1 Implement threat detector orchestrator and sub-detectors
    - Create `threat/detector.py`: ThreatDetector orchestrator with weighted session-level threat score aggregation
    - Create `threat/prompt_injection.py`: PromptInjectionDetector — pattern-based detection of embedded instructions in tool inputs/outputs
    - Create `threat/tool_poisoning.py`: ToolPoisoningDetector — schema/statistical deviation detection in tool responses
    - Create `threat/privilege_escalation.py`: PrivilegeEscalationDetector — scope creep analysis across action sequences
    - Create `threat/covert_channel.py`: CovertChannelDetector — steganographic encoding, base64 payload, unusual character detection
    - Create `threat/attack_chain.py`: AttackChainAnalyzer — sliding window (50 actions), cumulative effect model, STAC defense, kill chain generation
    - Target: each action evaluated within 50ms
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14_

  - [ ]* 5.2 Write property test for threat score aggregation bounds
    - **Property 10: Threat Score Aggregation Bounds** — session-level threat score is always in [0.0, 1.0] and recent actions contribute more weight
    - **Validates: Requirements 3.8**

- [ ] 6. Cryptographic audit trail
  - [ ] 6.1 Implement hash chain audit trail
    - Create `audit/hash_chain.py`: SHA-256 hash computation for audit entries (entry_id || timestamp || session_id || agent_identity_hash || action_parameters_hash || action_verdict || previous_entry_hash)
    - Create `audit/trail.py`: CryptographicAuditTrail — append entries with hash chain linking, monotonic sequence numbers per session, integrity verification, retry logic (3 retries, halt session on failure)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.8, 6.9_

  - [ ]* 6.2 Write property tests for audit trail integrity
    - **Property 2: Hash Chain Integrity** — for any sequence of appended entries, recomputing the hash chain from entry 1 to N produces hashes matching all stored entry_hash values
    - **Property 3: Monotonic Sequence Numbers** — within any session, sequence numbers are strictly monotonically increasing with no gaps
    - **Validates: Requirements 6.2, 6.8**

  - [ ] 6.3 Implement evidence package export
    - Create `audit/evidence.py`: EvidencePackage generation — export session/time-range audit entries with hash chain proof, chain of custody, and digital signature
    - _Requirements: 6.6, 6.7_

  - [ ] 6.4 Implement audit trail API routes
    - Create `api/routes_session.py`: GET /api/v1/sessions/{session_id}/audit-trail with hash_chain_valid verification
    - _Requirements: 6.4, 6.6_

- [ ] 7. Zero Trust evaluation pipeline
  - [ ] 7.1 Implement the 10-stage evaluation pipeline
    - Create `core/pipeline.py`: EvalPipeline with stages — auth, cap_token, dsl_policy, threat, dpdp, ethics, pii_mask, reasoning, grounding, attestation
    - Implement short-circuit logic: BLOCK/ESCALATE/QUARANTINE halts pipeline immediately
    - Implement FLAG handling: permit action, record warning
    - Implement QUARANTINE handling: block action, suspend session, preserve state
    - Generate ActionAttestation (signed with KavachAI Ed25519 key) on ALLOW
    - Record audit entry and update trust score after each evaluation
    - Publish dashboard events via Redis pub/sub
    - Target: <100ms total latency under normal conditions
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

  - [ ]* 7.2 Write property test for pipeline short-circuit
    - **Property 6: Pipeline Short-Circuit** — when any stage returns BLOCK/ESCALATE/QUARANTINE, no subsequent stage executes and the final verdict matches the blocking stage's verdict
    - **Validates: Requirements 5.2, 5.3**

  - [ ] 7.3 Implement core evaluation API route
    - Create POST /api/v1/evaluate endpoint in `api/routes_eval.py`
    - Accept ActionRequest body, run through EvalPipeline, return ActionVerdict
    - _Requirements: 5.1, 11.1_

- [ ] 8. Checkpoint — Core pipeline end-to-end working
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. DPDP compliance and PII masking
  - [ ] 9.1 Implement PII masker
    - Create `compliance/pii_masker.py`: regex-based detection and masking for Aadhaar (12-digit, optional spaces → XXXX XXXX 1234), PAN (ABCDE1234F), Indian mobile (+91, 10-digit), UPI IDs (name@bank), email addresses
    - _Requirements: 4.4, 4.5_

  - [ ]* 9.2 Write property test for PII masking completeness
    - **Property 5: PII Masking Completeness** — for any string containing Aadhaar/PAN/mobile patterns, the masked output contains zero instances of the original PII values
    - **Validates: Requirements 4.4**

  - [ ] 9.3 Implement DPDP compliance engine
    - Create `compliance/dpdp_engine.py`: consent record verification, data localization rule enforcement, breach notification trigger, processing register, data retention policies
    - _Requirements: 4.1, 4.2, 4.3, 4.6, 4.7, 4.8, 4.9_

  - [ ] 9.4 Implement compliance API routes
    - Create `api/routes_compliance.py`: GET /api/v1/compliance/dpdp-status, POST /api/v1/incidents/{incident_id}/export, GET /api/v1/incidents/{incident_id}/report
    - _Requirements: 4.6, 10.1, 10.2_

- [ ] 10. Dynamic trust scoring and DFA engine
  - [ ] 10.1 Implement trust scoring engine
    - Create `core/trust_engine.py`: dynamic trust score computation with severity-weighted violations, time-based decay, graduated enforcement (TRUSTED/STANDARD/RESTRICTED/QUARANTINED thresholds)
    - Store trust scores in Redis for fast lookup
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6_

  - [ ] 10.2 Implement DFA behavioral model engine
    - Create `core/dfa_engine.py`: load DFA models (states, transitions), track current state per session in Redis, validate tool-call transitions, compute path correctness and harmful call rate
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

- [ ] 11. Escalation manager
  - [ ] 11.1 Implement escalation manager
    - Create escalation logic in pipeline: Redis sorted set queue (scored by threat_score), configurable timeouts per policy rule (default 60s), safe default on timeout (BLOCK), duplicate request prevention
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [ ] 11.2 Implement escalation API routes
    - Create `api/routes_escalation.py`: GET /api/v1/escalations, POST /api/v1/escalations/{escalation_id}/resolve
    - _Requirements: 8.2, 8.3_

- [ ] 12. MCP Proxy Gateway and Safety Server
  - [ ] 12.1 Implement MCP Proxy Gateway
    - Create `mcp/proxy.py`: MCPProxyGateway — transparent proxy between MCP clients and servers
    - Implement handle_tools_list: aggregate tools from downstream servers, filter by capability token, attach capability labels
    - Implement handle_tools_call: intercept tool calls, build ActionRequest, run EvalPipeline, forward on ALLOW, error on BLOCK, hold on ESCALATE
    - Create `mcp/transport.py`: stdio and SSE transport support
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8_

  - [ ] 12.2 Implement MCP Safety Server
    - Create `mcp/safety_server.py`: MCPSafetyServer exposing 5 tools — check_policy (dry-run eval), get_my_permissions, request_escalation, get_compliance_status, report_suspicious_input
    - Authenticate all calls via agent identity
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6_

- [ ] 13. Checkpoint — Full backend pipeline with MCP proxy working
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Demo scenario — Multi-stage financial services attack
  - [ ] 14.1 Create demo policies and data
    - Create `demo/demo_policies.shield`: financial services DSL policies (block unauthorized payment, temporal data access restriction, prevent Aadhaar exfiltration, always mask PII)
    - Create `demo/demo_dfa.shield`: customer service DFA workflow (start → authenticated → data_accessed → response_sent, with dangerous admin_access state)
    - Create `demo/demo_knowledge_graph.json`: financial services knowledge graph (accounts, customers, transactions)
    - Create `demo/demo_ontology.json`: financial services domain ontology
    - _Requirements: 13.1, 13.2_

  - [ ] 14.2 Implement demo agent and attack scenario
    - Create `demo/demo_agent.py`: simulated financial services AI agent with tools (verify_identity, customer_lookup, payment_process, send_email, external_api, admin_panel)
    - Create `demo/scenario.py`: orchestrate the 5-stage attack — (1) indirect prompt injection via crafted customer message, (2) attempted Aadhaar exfiltration through API response, (3) privilege escalation to admin tools, (4) covert data channeling via steganographic encoding, (5) STAC sequential tool attack chain
    - Each stage should trigger KavachAI detection and produce visible verdicts (BLOCK/ESCALATE/QUARANTINE)
    - Generate kill chain visualization data for the dashboard
    - _Requirements: 13.3, 13.4, 13.5, 13.6, 13.7, 13.8_

  - [ ] 14.3 Create demo launch script
    - Create a launch script that starts the demo agent, connects through MCP Proxy Gateway, and triggers the attack scenario
    - Support both cloud-hosted and local Docker modes via environment flag
    - _Requirements: 20.7, 20.8_

- [ ] 15. WebSocket real-time feed
  - [ ] 15.1 Implement WebSocket dashboard endpoint
    - Create `api/websocket.py`: WS /ws/dashboard with X-API-Key auth
    - Subscribe to Redis pub/sub channel per tenant
    - Push event types: threat_update, escalation, kill_chain, quarantine, trust_change, grounding_alert, model_drift, safety_degradation, budget_warning
    - _Requirements: 9.1, 9.2, 9.3_

- [ ] 16. SOC Dashboard — React frontend
  - [ ] 16.1 Scaffold Next.js dashboard project
    - Create `kavachai/dashboard/` with Next.js 14, React 18, TailwindCSS, Recharts, Zustand
    - Create `hooks/useWebSocket.ts`: real-time WebSocket connection hook
    - Create `hooks/useApi.ts`: REST API client hook
    - Create `types/`: TypeScript type definitions matching backend Pydantic models
    - Create shared components: VerdictChip, ThreatScoreBadge, TrustLevelBadge, HashChainIndicator
    - _Requirements: 9.1, 9.2, 20.2_

  - [ ] 16.2 Implement Threat Feed page
    - Create ThreatFeedPage: LiveSessionTable (sortable by threat_score), ThreatScoreGauge, AlertPanel (quarantine/escalation/hash violations), RealTimeChart (actions/sec, threats/min)
    - _Requirements: 9.3, 9.4, 9.5_

  - [ ] 16.3 Implement Kill Chain visualization page
    - Create KillChainPage: KillChainGraph (directed graph with D3.js), StageDetailPanel, STACAttackIndicator, TimelineView
    - _Requirements: 9.6, 13.7_

  - [ ] 16.4 Implement Escalation page
    - Create EscalationPage: EscalationQueue (sorted by threat_score), EscalationDetailPanel (ActionRequest, ThreatAnalysis, KillChainContext, ComplianceImpact), ApproveRejectButtons
    - _Requirements: 8.1, 8.7, 9.7_

  - [ ] 16.5 Implement Forensic Investigation page
    - Create ForensicPage: SessionSelector, ActionTimeline (step-by-step replay), ActionDetailPanel (AttestationView, ReasoningTraceView with 3 layers, CapabilityTokenView, GroundingDetailView), EvidenceExportButton
    - _Requirements: 9.8, 9.9, 17.3, 26.3_

  - [ ] 16.6 Implement Compliance page
    - Create CompliancePage: DPDPStatusCard (consent, localization, PII masking), SevenSutrasRadarChart, ComplianceTrendChart, ExportReportButton
    - _Requirements: 9.10, 24.3, 24.5_

  - [ ] 16.7 Implement Agents and Policy pages
    - Create AgentsPage: AgentTable (trust score, level, status), TrustScoreHistory chart, AgentRegistrationForm
    - Create PolicyPage: PolicyList, DSLEditor (Monaco-based with syntax highlighting), VerificationResultPanel
    - _Requirements: 9.11, 16.6_

- [ ] 17. Checkpoint — Demo scenario end-to-end with dashboard
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 18. Docker Compose and deployment configuration
  - [ ] 18.1 Create Docker and deployment files
    - Create `Dockerfile.backend`: Python 3.11 image, install requirements, expose ports 8000 and 3001
    - Create `Dockerfile.dashboard`: Node 18 image, build Next.js, serve with nginx
    - Create `docker-compose.yml`: kavachai (backend), redis, dashboard services with volumes and networking per design Section 12
    - Create `railway.toml` for Railway deployment
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6_

- [ ] 19. Ethics engine and India AI governance
  - [ ] 19.1 Implement ethics engine
    - Create `ethics/engine.py`: EthicsEngine orchestrator computing Ethics_Score from four dimensions
    - Create `ethics/bias_detector.py`: India-specific bias detection (gender, caste, religion, regional, socioeconomic) with configurable sensitivity
    - Create `ethics/toxicity_filter.py`: toxicity classification with score (0.0-1.0), block above threshold (default 0.7)
    - Create `ethics/fairness_monitor.py`: track behavior patterns across sessions, detect systematic unfairness
    - Create `ethics/content_safety.py`: configurable content safety categories per deployment context
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7, 22.8, 22.9, 22.10_

  - [ ] 19.2 Implement India AI Governance mapper
    - Create `compliance/seven_sutras.py`: map KavachAI capabilities to Seven Sutras, generate compliance reports with per-principle scoring (0-100%)
    - Create `api/routes_compliance.py` additions: GET /api/v1/compliance/seven-sutras
    - _Requirements: 24.1, 24.2, 24.4, 24.6_

- [ ] 20. LLM explainability and reasoning capture
  - [ ] 20.1 Implement reasoning capture and decision explanations
    - Create `explain/reasoning_capture.py`: LLMReasoningCapture — capture chain-of-thought from LLM, inject reasoning instruction into system prompts
    - Create `explain/decision_explanation.py`: generate 3-layer Decision_Explanation (LLM reasoning, policy evaluation, user-facing summary)
    - Create `explain/templates.py`: configurable ExplanationTemplates for technical, compliance, individual, and executive audiences
    - Support multilingual user-facing explanations (English, Hindi)
    - _Requirements: 26.1, 26.2, 26.4, 26.5, 26.6, 26.7, 26.8_

- [ ] 21. Semantic grounding layer
  - [ ] 21.1 Implement semantic grounding layer
    - Create `grounding/layer.py`: SemanticGroundingLayer — deterministic validation (no LLM dependency)
    - Create `grounding/schema_enforcer.py`: JSON schema validation for structured agent outputs
    - Create `grounding/claim_extractor.py`: extract factual claims from agent output (NLP/regex-based)
    - Create `grounding/knowledge_graph.py`: KG store with entity/fact verification, load from JSON/YAML or Neo4j
    - Create `grounding/ontology.py`: domain ontology validation (concept/constraint checking)
    - Create `grounding/deterministic_validator.py`: numerical consistency, date validity, entity existence, regulatory checks, cross-reference validation
    - Create `grounding/source_attribution.py`: link claims to knowledge sources
    - _Requirements: 31.1, 31.2, 31.3, 31.4, 31.5, 31.6, 31.7, 31.8, 31.10_

  - [ ]* 21.2 Write property tests for grounding layer
    - **Property 7: Grounding Score Bounds** — grounding score is always in [0.0, 1.0] and equals grounded_claims / total_claims
    - **Property 9: Schema Enforcement Idempotence** — validating the same output against the same schema always produces the same result
    - **Property 12: Deterministic Validator Consistency** — identical inputs produce identical results across multiple invocations
    - **Validates: Requirements 31.4, 31.3, 31.7**

  - [ ] 21.3 Implement grounding API routes
    - Create `api/routes_grounding.py`: GET /api/v1/sessions/{session_id}/grounding-report
    - _Requirements: 31.9_

- [ ] 22. LLM Gateway and provider integration
  - [ ] 22.1 Implement LLM Gateway with routing and fallback
    - Create `llm/gateway.py`: LLMGateway — unified API, intelligent routing (simple→cheap, complex→capable), fallback chains, budget enforcement
    - Create `llm/providers/openai.py`, `llm/providers/anthropic.py`, `llm/providers/google.py`, `llm/providers/ollama.py`: provider adapters
    - Create `llm/interceptor.py`: LLMRequestInterceptor — pre-scan prompts (injection, data leakage), post-scan responses (toxicity, bias, hallucination)
    - Create `llm/budget.py`: budget tracking per agent/session/org in Redis, BUDGET_EXCEEDED enforcement
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 21.8, 21.9, 21.10, 25.1, 25.2, 25.3, 25.4, 25.5_

  - [ ] 22.2 Implement LLM API routes
    - Create `api/routes_llm.py`: POST /api/v1/llm/completions, GET /api/v1/llm/models, GET /api/v1/llm/usage
    - _Requirements: 21.1, 25.6, 25.7_

- [ ] 23. Checkpoint — Full backend feature-complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 24. Hallucination detection and output validation
  - [ ] 24.1 Implement hallucination detector
    - Implement Hallucination_Detector: compare agent claims against ActionAttestation records, detect TOOL_FABRICATION (no attestation), RESULT_MISSTATEMENT (values differ), UNGROUNDED claims
    - Assign severity (LOW/MEDIUM/HIGH), block and escalate on HIGH severity
    - Wire into the evaluation pipeline's grounding stage
    - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5, 23.6, 23.7_

- [ ] 25. Multi-agent governance
  - [ ] 25.1 Implement multi-agent governor
    - Create `multi_agent/governor.py`: MultiAgentGovernor — enforce delegation chain depth limits (default 3), prevent privilege amplification
    - Create `multi_agent/delegation.py`: track delegation chains (delegator, receiver, task, permissions)
    - Create `multi_agent/collusion.py`: CollusionDetector — cross-session action graph, detect coordinated policy circumvention
    - Record all inter-agent communications in audit trail
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

- [ ] 26. LLM evaluation and model transparency (advanced)
  - [ ] 26.1 Implement LLM evaluation engine
    - Create `llm/eval_engine.py`: LLMEvalEngine — run configurable SafetyBenchmarks (prompt injection, toxicity, bias, hallucination, accuracy, domain-specific), compute ModelSafetyScore (0-100)
    - Create `llm/red_team.py`: RedTeamRunner — automated adversarial testing with attack generators (prompt injection, jailbreak, bias trigger)
    - Block models below safety threshold (default 70) from gateway
    - _Requirements: 30.1, 30.2, 30.3, 30.4, 30.5, 30.6, 30.7_

  - [ ]* 26.2 Write property test for model safety score aggregation
    - **Property 8: Model Safety Score Aggregation** — overall score is always in [0, 100] and equals weighted sum of sub-scores
    - **Validates: Requirements 30.2**

  - [ ] 26.3 Implement LLM observability and model transparency
    - Create `llm/observability.py`: LLMObservability — track latency (p50/p95/p99), error rate, refusal rate, response quality; ModelDriftDetector with baseline comparison and drift alerts
    - Implement Model_Card storage and Model_Provenance_Record in audit trail
    - _Requirements: 27.1, 27.2, 27.4, 27.6, 28.1, 28.2, 28.3, 28.4, 28.6_

  - [ ] 26.4 Implement LLM evaluation API routes
    - Create additions to `api/routes_llm.py`: POST /api/v1/llm/evaluate/{model_name}, POST /api/v1/llm/red-team/{model_name}, GET /api/v1/llm/evaluations/{model_name}/history, GET /api/v1/llm/compare
    - _Requirements: 30.6, 30.8_

- [ ] 27. Advanced dashboard pages (nice-to-have)
  - [ ] 27.1 Implement Model Evaluation and LLM Usage dashboard pages
    - Create ModelEvaluationPage: SafetyScoreOverview, BenchmarkBreakdownChart, HistoricalScoreTrend, HeadToHeadComparison, RedTeamResultsPanel
    - Create LLMUsagePage: CostDashboard, BudgetUtilizationGauge, TokenUsageChart, ModelHealthPanel (traffic lights), DriftAlertList
    - _Requirements: 25.6, 27.3, 28.5, 30.8_

  - [ ] 27.2 Implement Grounding Reports and Model Registry dashboard pages
    - Create GroundingReportsPage: SessionGroundingTable, ClaimVerificationList, DeterministicCheckResults, UngroundedClaimsHighlight
    - Create ModelRegistryPage: ModelCardList, ModelCardDetail, ModelPerformanceChart
    - _Requirements: 23.8, 27.3, 31.9_

- [ ] 28. Determinism assurance and replay
  - [ ] 28.1 Implement determinism audit replay
    - Create `audit/replay.py`: session replay — re-execute action sequences, compare trajectories, compute trajectory determinism and decision determinism scores, generate DeterminismReport
    - Create API: POST /api/v1/sessions/{session_id}/replay
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_

- [ ] 29. Formal policy verification (advanced, optional)
  - [ ] 29.1 Implement formal policy verifier
    - Create `core/formal_verifier.py`: offline verification of DSL policies — check consistency (no conflicting rules), completeness (all tool calls covered), generate verification certificates
    - Create API: POST /api/v1/policies/{policy_id}/verify
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_

- [ ] 30. Law enforcement integration (advanced, optional)
  - [ ] 30.1 Implement CERT-In reporting and incident export
    - Create `compliance/cert_in.py`: format incident data for CERT-In submission, auto-generate structured incident reports
    - Implement signed evidence package export for law enforcement
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 31. Multi-tenant enterprise features (advanced, optional)
  - [ ] 31.1 Implement tenant isolation
    - Add tenant_id scoping to all database queries and Redis keys
    - Implement tenant-level API key authentication, rate limits, LLM gateway configuration
    - Create tenants table management and super-admin cross-tenant aggregate views
    - _Requirements: 29.1, 29.2, 29.3, 29.4, 29.5, 29.6, 29.7_

- [ ] 32. Final checkpoint — Complete system integration
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Tasks 1-17 form the critical path for a working hackathon demo (core pipeline + demo scenario + dashboard)
- Tasks 18-23 complete the full backend feature set
- Tasks 24-31 are advanced features — implement if time permits
- The demo scenario (Task 14) is the highest-priority deliverable after the core pipeline
- Each task references specific requirements for traceability
- Checkpoints at tasks 3, 8, 13, 17, 23, and 32 ensure incremental validation
- Property tests validate universal correctness properties from design Section 18
