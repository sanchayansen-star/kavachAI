# KavachAI — Enterprise Production Plan

> A detailed guide for deploying KavachAI in a production enterprise environment on AWS, applying the AWS Well-Architected Framework across all six pillars.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Production Architecture on AWS](#2-production-architecture-on-aws)
3. [AWS Services Mapping](#3-aws-services-mapping)
4. [AWS Well-Architected Framework Application](#4-aws-well-architected-framework-application)
5. [Infrastructure as Code](#5-infrastructure-as-code)
6. [CI/CD Pipeline](#6-cicd-pipeline)
7. [Database Strategy](#7-database-strategy)
8. [Networking and Security](#8-networking-and-security)
9. [Observability and Monitoring](#9-observability-and-monitoring)
10. [Disaster Recovery and Business Continuity](#10-disaster-recovery-and-business-continuity)
11. [Cost Estimation](#11-cost-estimation)
12. [Rollout Plan](#12-rollout-plan)
13. [Operational Runbook](#13-operational-runbook)

---

## 1. Executive Summary

This document describes how to take KavachAI from its current hackathon prototype to a
production-grade enterprise deployment on AWS. The plan covers infrastructure, security,
compliance, observability, cost, and a phased rollout strategy.

### Current State vs. Production Target

| Aspect | Hackathon (Current) | Enterprise Production |
|--------|--------------------|-----------------------|
| Compute | Single process (uvicorn) | ECS Fargate auto-scaling cluster |
| Database | SQLite (single file) | Amazon Aurora PostgreSQL (multi-AZ) |
| Cache | Single Redis instance | Amazon ElastiCache Redis (clustered) |
| Storage | Local filesystem | S3 + EFS for evidence packages |
| Auth | Static API key | Amazon Cognito + IAM + API Gateway |
| Secrets | .env file | AWS Secrets Manager |
| CDN | None | CloudFront |
| DNS | localhost | Route 53 |
| Monitoring | Console logs | CloudWatch + X-Ray + Prometheus |
| CI/CD | Manual | CodePipeline + CodeBuild + ECR |
| IaC | docker-compose.yml | AWS CDK (TypeScript) |


---

## 2. Production Architecture on AWS

```
                                    ┌─────────────────────────────────┐
                                    │         Route 53 (DNS)          │
                                    │   kavachai.example.com          │
                                    └───────────────┬─────────────────┘
                                                    │
                                    ┌───────────────▼─────────────────┐
                                    │     CloudFront (CDN/WAF)        │
                                    │  - Static dashboard assets      │
                                    │  - DDoS protection (Shield)     │
                                    │  - WAF rules                    │
                                    └──────┬──────────────┬───────────┘
                                           │              │
                              ┌────────────▼──┐    ┌──────▼──────────┐
                              │  S3 Bucket    │    │  API Gateway    │
                              │  (Dashboard   │    │  (REST + WS)   │
                              │   static)     │    │  - Rate limiting│
                              │               │    │  - Auth (Cognito│
                              └───────────────┘    │  - Throttling   │
                                                   └───────┬─────────┘
                                                           │
                              ┌─────────────────── VPC ────┼──────────────────────┐
                              │                            │                      │
                              │  ┌─────────────────────────▼───────────────────┐  │
                              │  │        Application Load Balancer (ALB)      │  │
                              │  │  - Health checks  - SSL termination         │  │
                              │  │  - Path routing: /api/* → backend           │  │
                              │  │                  /ws/*  → websocket          │  │
                              │  │                  /mcp/* → mcp-proxy         │  │
                              │  └──────┬──────────────┬──────────────┬────────┘  │
                              │         │              │              │            │
                              │  ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼────────┐  │
                              │  │ ECS Fargate  │ │ECS Fargate │ │ECS Fargate  │  │
                              │  │ Backend      │ │WebSocket   │ │MCP Proxy    │  │
                              │  │ Service      │ │Service     │ │Service      │  │
                              │  │ (2-10 tasks) │ │(2-4 tasks) │ │(2-6 tasks)  │  │
                              │  └──────┬───┬───┘ └─────┬──────┘ └────┬────────┘  │
                              │         │   │           │             │            │
                              │  ┌──────▼───▼───────────▼─────────────▼────────┐  │
                              │  │              Private Subnets                 │  │
                              │  │                                              │  │
                              │  │  ┌──────────────┐    ┌───────────────────┐   │  │
                              │  │  │ ElastiCache  │    │  Aurora PostgreSQL│   │  │
                              │  │  │ Redis Cluster│    │  (Multi-AZ)      │   │  │
                              │  │  │ (3 nodes)    │    │  Writer + Reader │   │  │
                              │  │  └──────────────┘    └───────────────────┘   │  │
                              │  │                                              │  │
                              │  │  ┌──────────────┐    ┌───────────────────┐   │  │
                              │  │  │ S3 Bucket    │    │ Secrets Manager   │   │  │
                              │  │  │ (Evidence    │    │ (API keys, LLM   │   │  │
                              │  │  │  Packages)   │    │  keys, Ed25519)  │   │  │
                              │  │  └──────────────┘    └───────────────────┘   │  │
                              │  └──────────────────────────────────────────────┘  │
                              └───────────────────────────────────────────────────┘
```

### Service Separation

The monolithic FastAPI app is split into three ECS services for independent scaling:

| Service | Responsibility | Scaling Trigger |
|---------|---------------|-----------------|
| Backend API | REST endpoints, evaluation pipeline, policy engine | CPU > 60% or request count |
| WebSocket | Real-time dashboard feed, pub/sub relay | Connection count |
| MCP Proxy | MCP protocol gateway, tool call interception | Request latency p95 > 100ms |


---

## 3. AWS Services Mapping

Every KavachAI component maps to a specific AWS service. Here is the complete mapping:

### Compute

| Component | AWS Service | Configuration |
|-----------|------------|---------------|
| Backend API | ECS Fargate | 0.5 vCPU / 1 GB per task, 2-10 tasks auto-scaling |
| WebSocket Service | ECS Fargate | 0.25 vCPU / 0.5 GB per task, 2-4 tasks |
| MCP Proxy Gateway | ECS Fargate | 0.5 vCPU / 1 GB per task, 2-6 tasks |
| Container Registry | ECR | Private repository per service |
| Task Scheduling | ECS Service Auto Scaling | Target tracking on CPU and request count |

### Database and Storage

| Component | AWS Service | Configuration |
|-----------|------------|---------------|
| Audit Trail (replaces SQLite) | Aurora PostgreSQL Serverless v2 | 0.5-8 ACU, Multi-AZ, encrypted at rest |
| Session State / Cache | ElastiCache Redis | r6g.large, 3-node cluster, encryption in transit |
| Evidence Packages | S3 | Versioned bucket, S3 Object Lock (WORM), lifecycle to Glacier after 1 year |
| DSL Policy Files | S3 | Versioned bucket for policy source and compiled ASTs |
| Knowledge Graphs | S3 + DynamoDB | S3 for bulk storage, DynamoDB for fast entity lookups |
| Dashboard Static Assets | S3 | Static website hosting behind CloudFront |

### Networking

| Component | AWS Service | Configuration |
|-----------|------------|---------------|
| DNS | Route 53 | Hosted zone with health checks and failover routing |
| CDN | CloudFront | Edge caching for dashboard, WebSocket passthrough |
| Load Balancer | ALB | Path-based routing, SSL termination, sticky sessions for WS |
| VPC | VPC | 3 AZs, public + private subnets, NAT Gateway |
| Firewall | WAF | Rate limiting, SQL injection protection, geo-blocking |
| DDoS Protection | Shield Standard | Automatic L3/L4 protection (included with CloudFront) |

### Security and Identity

| Component | AWS Service | Configuration |
|-----------|------------|---------------|
| User Authentication (Dashboard) | Cognito User Pool | MFA enabled, password policies |
| API Authentication | API Gateway + Cognito Authorizer | JWT validation, per-tenant API keys |
| Agent Key Management | KMS | CMK for Ed25519 key wrapping, automatic rotation |
| Secrets (LLM keys, DB creds) | Secrets Manager | Automatic rotation every 30 days |
| Certificate Management | ACM | Auto-renewing TLS certificates |
| Network Isolation | Security Groups + NACLs | Least-privilege ingress/egress rules |
| Audit Logging | CloudTrail | All API calls logged, S3 delivery with integrity validation |

### Observability

| Component | AWS Service | Configuration |
|-----------|------------|---------------|
| Application Logs | CloudWatch Logs | Structured JSON, 90-day retention |
| Metrics | CloudWatch Metrics | Custom metrics for pipeline latency, threat scores |
| Distributed Tracing | X-Ray | Trace every evaluation pipeline execution |
| Dashboards | CloudWatch Dashboards | Operational and business metrics |
| Alerting | CloudWatch Alarms + SNS | PagerDuty/Slack integration for critical alerts |
| Uptime Monitoring | Route 53 Health Checks | /health endpoint every 30s from 3 regions |

### CI/CD

| Component | AWS Service | Configuration |
|-----------|------------|---------------|
| Source | CodeCommit or GitLab mirroring | Webhook triggers on push to main |
| Build | CodeBuild | Docker image build, unit tests, security scanning |
| Container Scanning | ECR Image Scanning | Scan on push, block critical CVEs |
| Deploy | CodeDeploy (ECS) | Blue/green deployment with automatic rollback |
| Pipeline Orchestration | CodePipeline | Source → Build → Test → Staging → Production |
| Infrastructure | CDK (TypeScript) | All infrastructure defined as code |


---

## 4. AWS Well-Architected Framework Application

### Pillar 1: Operational Excellence

This pillar focuses on running and monitoring systems to deliver business value and continually improving processes.

#### Design Principles Applied

- **Perform operations as code:** All infrastructure is defined in AWS CDK (TypeScript). No manual console changes. Every environment (dev, staging, prod) is reproducible from code.

- **Make frequent, small, reversible changes:** Blue/green deployments via CodeDeploy. Each service is independently deployable. A bad deployment rolls back automatically if health checks fail within 5 minutes.

- **Refine operations procedures frequently:** Operational runbooks are stored in SSM Documents. Post-incident reviews update runbooks automatically.

- **Anticipate failure:** Chaos engineering with AWS Fault Injection Simulator. Monthly game days simulating Redis failure, database failover, and AZ outage.

- **Learn from all operational failures:** Every incident creates a CloudWatch Insights query that becomes a permanent alarm.

#### Specific Implementations

| Practice | Implementation |
|----------|---------------|
| Deployment automation | CodePipeline: GitLab push → CodeBuild (test + build) → ECR → CodeDeploy (blue/green) |
| Configuration management | SSM Parameter Store for feature flags, Secrets Manager for credentials |
| Operational health | CloudWatch composite alarms: pipeline latency p95 < 100ms, error rate < 1%, audit chain integrity 100% |
| Runbook automation | SSM Automation documents for common operations: scale up, rotate keys, flush cache, export evidence |
| On-call | PagerDuty integration via SNS. Escalation: L1 (auto-remediation) → L2 (on-call engineer) → L3 (security lead) |

### Pillar 2: Security

This is the most critical pillar for KavachAI — the product itself is a security tool.

#### Design Principles Applied

- **Implement a strong identity foundation:** Every entity has a unique identity. Human operators use Cognito with MFA. AI agents use Ed25519 key pairs managed by KMS. Service-to-service uses IAM roles (no long-lived credentials).

- **Enable traceability:** CloudTrail logs every AWS API call. KavachAI's own audit trail records every agent action with SHA-256 hash chains. X-Ray traces every pipeline execution. All logs are immutable (S3 Object Lock).

- **Apply security at all layers:** WAF at the edge, Security Groups at the network layer, IAM at the service layer, Cognito at the application layer, KavachAI's own policy engine at the agent layer.

- **Automate security best practices:** GuardDuty for threat detection, Inspector for vulnerability scanning, Config for compliance rules, SecurityHub for unified view.

- **Protect data in transit and at rest:** TLS 1.3 everywhere (ACM certificates). AES-256 encryption at rest for Aurora, ElastiCache, S3, and EBS. KMS CMKs with automatic rotation.

- **Keep people away from data:** No SSH access to containers (Fargate). Database access only through application layer. Evidence packages are WORM-protected (S3 Object Lock).

- **Prepare for security events:** Incident response plan with automated containment. KavachAI's CERT-In reporting generates structured incident reports automatically.

#### Specific Implementations

| Layer | Controls |
|-------|----------|
| Edge | CloudFront + WAF (rate limiting, geo-blocking, OWASP rules) + Shield |
| Network | VPC with private subnets, no public IPs on compute, NAT Gateway for outbound |
| Compute | Fargate (no OS access), ECR image scanning, read-only root filesystem |
| Application | Cognito JWT validation, per-tenant API keys, RBAC for dashboard |
| Data | Aurora encryption (KMS), ElastiCache encryption in transit, S3 SSE-KMS |
| Agent | Ed25519 identity, capability tokens, trust scoring, policy enforcement |
| Audit | CloudTrail + KavachAI hash chain + S3 Object Lock (immutable evidence) |
| Secrets | Secrets Manager with 30-day rotation, no secrets in environment variables |
| Compliance | AWS Config rules for CIS benchmarks, SecurityHub for unified findings |

#### Data Classification

| Data Type | Classification | Storage | Encryption | Retention | Jurisdiction Notes |
|-----------|---------------|---------|------------|-----------|-------------------|
| Audit entries (hash chain) | Confidential | Aurora + S3 backup | AES-256 (KMS) | 7 years (regulatory) | Stored in tenant's jurisdiction region |
| Evidence packages | Restricted | S3 Object Lock (WORM) | AES-256 (KMS) | 7 years | Region-locked per jurisdiction |
| Agent private keys | Secret | KMS (never leaves HSM) | KMS CMK | Until revoked | Region-specific KMS keys |
| PII (pre-masking) | Restricted | In-memory only | TLS in transit | Never persisted | GDPR: right to erasure applies |
| DSL policies | Internal | S3 + Aurora | AES-256 | Versioned indefinitely | May contain jurisdiction-specific rules |
| Dashboard sessions | Internal | Cognito + ElastiCache | TLS + AES-256 | 24 hours | — |
| LLM API keys | Secret | Secrets Manager | KMS CMK | Until rotated | — |
| GDPR consent records | Confidential | Aurora | AES-256 (KMS) | Duration of processing + 3 years | EU region only (eu-west-1) |
| GDPR erasure requests | Confidential | Aurora | AES-256 (KMS) | 3 years after completion | EU region only |
| FCA/PRA compliance records | Confidential | Aurora + S3 backup | AES-256 (KMS) | 7 years (FCA requirement) | UK region only (eu-west-2) |
| SM&CR accountability maps | Restricted | Aurora | AES-256 (KMS) | Duration of appointment + 6 years | UK region only |
| Cross-border transfer logs | Confidential | Aurora | AES-256 (KMS) | 5 years | Stored in originating region |

### Pillar 3: Reliability

#### Design Principles Applied

- **Automatically recover from failure:** ECS service auto-recovery restarts failed tasks. Aurora Multi-AZ provides automatic database failover (< 30s). ElastiCache automatic failover for Redis.

- **Test recovery procedures:** Monthly DR drills. Automated failover testing with Fault Injection Simulator.

- **Scale horizontally:** Each ECS service scales independently. Aurora Serverless v2 scales compute automatically. ElastiCache scales read replicas.

- **Stop guessing capacity:** Auto-scaling policies based on actual metrics (CPU, request count, connection count). Aurora Serverless eliminates database capacity planning.

- **Manage change in automation:** All changes through CodePipeline. No manual deployments.

#### Specific Implementations

| Failure Scenario | Recovery Mechanism | RTO | RPO |
|-----------------|-------------------|-----|-----|
| Single task crash | ECS auto-restart + ALB health check deregistration | < 30s | 0 |
| AZ failure | Multi-AZ ALB + Aurora failover + ElastiCache failover | < 60s | 0 |
| Region failure | Route 53 failover to DR region (Aurora Global Database) | < 15 min | < 1 min |
| Database corruption | Aurora point-in-time recovery (5-min granularity) | < 30 min | < 5 min |
| Redis failure | ElastiCache automatic failover + application retry | < 30s | Session state loss (acceptable) |
| Bad deployment | CodeDeploy automatic rollback on health check failure | < 5 min | 0 |
| DDoS attack | Shield + WAF rate limiting + CloudFront absorption | Automatic | 0 |

#### Availability Target

- **SLA:** 99.95% uptime (< 4.38 hours downtime per year)
- **Pipeline latency SLO:** p95 < 100ms, p99 < 250ms
- **Audit trail integrity:** 100% (any hash chain break triggers immediate alert)

### Pillar 4: Performance Efficiency

#### Design Principles Applied

- **Democratize advanced technologies:** Fargate eliminates server management. Aurora Serverless eliminates database tuning. Managed Redis eliminates cache operations.

- **Go global in minutes:** CloudFront edge locations serve the dashboard globally. API Gateway edge-optimized endpoints reduce latency for distributed agents.

- **Use serverless architectures:** Fargate (serverless compute), Aurora Serverless v2 (serverless database), S3 (serverless storage).

- **Experiment more often:** Feature flags in SSM Parameter Store allow A/B testing of new pipeline stages without deployment.

#### Performance Targets and Optimizations

| Component | Target | Optimization |
|-----------|--------|-------------|
| Evaluation pipeline | p95 < 100ms | In-memory policy engine, Redis for session state, connection pooling |
| DSL policy parsing | < 10ms per rule | Pre-compiled ASTs cached in memory, hot reload from S3 |
| Threat detection | < 50ms per action | Parallel sub-detector execution, pre-compiled regex patterns |
| Audit trail append | < 20ms | Aurora with connection pooling (asyncpg), batch writes for high throughput |
| Dashboard load | < 2s initial, < 200ms navigation | CloudFront CDN, Next.js static generation, code splitting |
| WebSocket latency | < 100ms event delivery | ElastiCache pub/sub, ALB sticky sessions |
| MCP proxy overhead | < 50ms added latency | Direct memory pipeline (no HTTP hop), connection reuse |

#### Caching Strategy

```
Layer 1: CloudFront (dashboard static assets, API responses with Cache-Control)
Layer 2: ElastiCache Redis
  - Agent trust scores (TTL: 60s)
  - Capability tokens (TTL: until expiry)
  - Session state (TTL: session duration)
  - Compiled policy ASTs (TTL: until policy update)
  - Rate limit counters (TTL: window duration)
Layer 3: Application memory
  - Loaded PolicyAST objects
  - Pre-compiled regex patterns for threat detection
  - DFA state machines
```

### Pillar 5: Cost Optimization

#### Design Principles Applied

- **Implement cloud financial management:** AWS Cost Explorer + Budgets with alerts at 50%, 80%, 100% of monthly target.

- **Adopt a consumption model:** Fargate (pay per task-second), Aurora Serverless (pay per ACU-second), S3 (pay per GB stored + requests).

- **Measure overall efficiency:** Cost per evaluation (target: < $0.001 per pipeline execution).

- **Stop spending money on undifferentiated heavy lifting:** Managed services for database, cache, CDN, DNS, certificates, secrets.

#### Cost Estimation (Monthly, ap-south-1 Mumbai Region)

| Service | Configuration | Estimated Monthly Cost |
|---------|--------------|----------------------|
| ECS Fargate (Backend) | 4 tasks avg × 0.5 vCPU × 1 GB | $58 |
| ECS Fargate (WebSocket) | 2 tasks avg × 0.25 vCPU × 0.5 GB | $14 |
| ECS Fargate (MCP Proxy) | 3 tasks avg × 0.5 vCPU × 1 GB | $44 |
| Aurora Serverless v2 | 2 ACU avg, Multi-AZ, 50 GB storage | $145 |
| ElastiCache Redis | r6g.large, 3 nodes | $290 |
| S3 (evidence + policies) | 100 GB, 1M requests | $3 |
| CloudFront | 100 GB transfer, 10M requests | $15 |
| ALB | 1 ALB, 10 LCU avg | $25 |
| API Gateway | 10M requests | $35 |
| Route 53 | 1 hosted zone, 10M queries | $5 |
| Secrets Manager | 10 secrets | $4 |
| CloudWatch | Logs (50 GB), metrics, alarms | $35 |
| X-Ray | 1M traces | $5 |
| WAF | 1 web ACL, 5 rules, 10M requests | $11 |
| KMS | 2 CMKs, 1M requests | $3 |
| NAT Gateway | 1 per AZ (3), 100 GB data | $100 |
| **Total** | | **~$792/month** |

#### Cost Optimization Levers

- **Reserved capacity:** Savings Plans for Fargate (up to 50% savings with 1-year commitment)
- **Right-sizing:** Start with smaller instances, scale based on actual usage
- **S3 lifecycle:** Move evidence packages to Glacier after 1 year (90% storage cost reduction)
- **NAT Gateway:** Consider VPC endpoints for S3 and ECR to reduce NAT costs
- **Spot Fargate:** Use Spot for non-critical batch workloads (red teaming, model evaluation)

### Pillar 6: Sustainability

#### Design Principles Applied

- **Understand your impact:** Tag all resources with `project:kavachai` and `environment:prod` for carbon footprint tracking.

- **Establish sustainability goals:** Target: reduce cost-per-evaluation by 20% year-over-year through efficiency improvements.

- **Maximize utilization:** Auto-scaling ensures compute matches demand. Aurora Serverless scales to zero during off-hours in non-prod environments.

- **Adopt more efficient hardware:** Graviton (ARM) instances for Fargate tasks (20% better price-performance, 60% less energy).

- **Reduce downstream impact:** Intelligent LLM routing sends simple queries to smaller, cheaper models (reducing energy consumption per inference).

#### Specific Implementations

| Practice | Implementation |
|----------|---------------|
| ARM compute | Fargate tasks on Graviton3 (arm64 Docker images) |
| Right-sized compute | 0.5 vCPU tasks instead of full vCPU (sufficient for < 100ms pipeline) |
| Serverless database | Aurora Serverless v2 scales to minimum during low traffic |
| Efficient caching | Redis reduces redundant database queries by 90% |
| LLM routing | Simple queries → gpt-3.5-turbo (less energy), complex → gpt-4 (only when needed) |
| Data lifecycle | S3 Intelligent-Tiering for evidence packages, Glacier for archives |


---

## 5. Infrastructure as Code

All infrastructure is defined using AWS CDK (TypeScript). The stack is organized into nested constructs:

```
kavachai-infra/
├── bin/
│   └── app.ts                    # CDK app entry point
├── lib/
│   ├── network-stack.ts          # VPC, subnets, NAT, security groups
│   ├── database-stack.ts         # Aurora Serverless, ElastiCache
│   ├── compute-stack.ts          # ECS cluster, Fargate services, ALB
│   ├── storage-stack.ts          # S3 buckets (evidence, policies, dashboard)
│   ├── security-stack.ts         # Cognito, KMS, WAF, Secrets Manager
│   ├── observability-stack.ts    # CloudWatch dashboards, alarms, X-Ray
│   ├── cicd-stack.ts             # CodePipeline, CodeBuild, CodeDeploy
│   └── dns-stack.ts              # Route 53, ACM certificates, CloudFront
├── cdk.json
└── package.json
```

### Environment Promotion

```
Feature Branch → Dev (auto-deploy on push)
                  ↓
              Staging (deploy on PR merge to main)
                  ↓ (manual approval gate)
              Production (blue/green with automatic rollback)
```

---

## 6. CI/CD Pipeline

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Source   │───►│  Build   │───►│  Test    │───►│ Staging  │───►│Production│
│ (GitLab) │    │(CodeBuild│    │          │    │ (Auto)   │    │(Approval)│
│          │    │ + ECR)   │    │          │    │          │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                     │               │
                     ▼               ▼
              Docker build      Unit tests
              ECR push          Integration tests
              ECR scan          Security scan (Bandit)
              CDK synth         Load test (k6)
```

### Build Stage Details

1. **Docker Build:** Multi-stage Dockerfile, Graviton (arm64) target, layer caching
2. **ECR Push:** Tagged with git SHA and `latest`
3. **ECR Scan:** Block deployment if critical or high CVEs found
4. **CDK Synth:** Generate CloudFormation templates, diff against current stack

### Test Stage Details

1. **Unit Tests:** pytest with coverage > 80% gate
2. **Integration Tests:** Spin up LocalStack, run API tests against real endpoints
3. **Security Scan:** Bandit (Python SAST), npm audit (dashboard), Trivy (container)
4. **Load Test:** k6 script simulating 1000 concurrent evaluations, verify p95 < 100ms

### Deployment Strategy

- **Blue/Green via CodeDeploy:** New version deployed alongside old. Traffic shifted after health checks pass. Automatic rollback if error rate > 1% within 5 minutes.
- **Database migrations:** Run as a pre-deployment ECS task. Backward-compatible migrations only (expand-contract pattern).
- **Feature flags:** SSM Parameter Store. New pipeline stages can be enabled per-tenant without deployment.

---

## 7. Database Strategy

### Migration from SQLite to Aurora PostgreSQL

The current SQLite schema maps directly to PostgreSQL with these enhancements:

| Enhancement | Reason |
|-------------|--------|
| JSONB columns (instead of TEXT for JSON) | Native JSON querying, indexing on JSON paths |
| Partitioned audit_entries table | Partition by month for query performance and data lifecycle |
| Read replicas | Separate read traffic (dashboard queries) from write traffic (audit appends) |
| Connection pooling (PgBouncer) | Handle 1000+ concurrent connections from Fargate tasks |
| Point-in-time recovery | 5-minute granularity, 35-day retention |

### Partitioning Strategy for Audit Trail

```sql
-- Partition audit_entries by month for performance and lifecycle management
CREATE TABLE audit_entries (
    entry_id        BIGSERIAL,
    timestamp       TIMESTAMPTZ NOT NULL,
    session_id      TEXT NOT NULL,
    tenant_id       TEXT NOT NULL,
    -- ... other columns ...
    entry_hash      TEXT NOT NULL,
    sequence_number BIGINT NOT NULL,
    PRIMARY KEY (entry_id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Auto-create monthly partitions
CREATE TABLE audit_entries_2026_03 PARTITION OF audit_entries
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
```

### Redis Data Architecture

```
Cluster: 3 nodes (1 primary + 2 replicas per shard)

Shard 1: Session state
  session:{id}:threat_score, session:{id}:dfa_state, session:{id}:action_window

Shard 2: Agent state + rate limiting
  agent:{id}:trust_score, rate:{id}:{tool}:{window}, token:{id}

Shard 3: Pub/sub + escalations
  channel:dashboard:{tenant_id}, escalation:queue, budget:{id}:cost
```

---

## 8. Networking and Security

### VPC Design

#### India Region (ap-south-1, Mumbai) — Primary for Indian tenants

```
VPC: 10.0.0.0/16 (ap-south-1, Mumbai)

AZ-a (ap-south-1a):
  Public:  10.0.1.0/24  (NAT Gateway, ALB)
  Private: 10.0.4.0/24  (ECS tasks)
  Data:    10.0.7.0/24  (Aurora, ElastiCache)

AZ-b (ap-south-1b):
  Public:  10.0.2.0/24  (NAT Gateway)
  Private: 10.0.5.0/24  (ECS tasks)
  Data:    10.0.8.0/24  (Aurora replica, ElastiCache replica)

AZ-c (ap-south-1c):
  Public:  10.0.3.0/24  (NAT Gateway)
  Private: 10.0.6.0/24  (ECS tasks)
  Data:    10.0.9.0/24  (ElastiCache replica)
```

#### EU Region (eu-west-1, Ireland) — Primary for EU/GDPR tenants

```
VPC: 10.1.0.0/16 (eu-west-1, Ireland)

AZ-a (eu-west-1a):
  Public:  10.1.1.0/24  (NAT Gateway, ALB)
  Private: 10.1.4.0/24  (ECS tasks)
  Data:    10.1.7.0/24  (Aurora, ElastiCache)

AZ-b (eu-west-1b):
  Public:  10.1.2.0/24  (NAT Gateway)
  Private: 10.1.5.0/24  (ECS tasks)
  Data:    10.1.8.0/24  (Aurora replica, ElastiCache replica)

AZ-c (eu-west-1c):
  Public:  10.1.3.0/24  (NAT Gateway)
  Private: 10.1.6.0/24  (ECS tasks)
  Data:    10.1.9.0/24  (ElastiCache replica)
```

#### UK Region (eu-west-2, London) — Primary for UK/FCA tenants

```
VPC: 10.2.0.0/16 (eu-west-2, London)

AZ-a (eu-west-2a):
  Public:  10.2.1.0/24  (NAT Gateway, ALB)
  Private: 10.2.4.0/24  (ECS tasks)
  Data:    10.2.7.0/24  (Aurora, ElastiCache)

AZ-b (eu-west-2b):
  Public:  10.2.2.0/24  (NAT Gateway)
  Private: 10.2.5.0/24  (ECS tasks)
  Data:    10.2.8.0/24  (Aurora replica, ElastiCache replica)
```

### Security Group Rules

| Security Group | Inbound | Outbound |
|---------------|---------|----------|
| ALB | 443 from 0.0.0.0/0 | All to ECS SG |
| ECS Tasks | 8000 from ALB SG | 5432 to Aurora SG, 6379 to Redis SG, 443 to NAT |
| Aurora | 5432 from ECS SG | None |
| ElastiCache | 6379 from ECS SG | None |

### DPDP Act Data Residency

For compliance with India's DPDP Act 2023:
- **Primary region:** ap-south-1 (Mumbai) — all data at rest stays in India
- **DR region:** ap-south-2 (Hyderabad) — encrypted replication within India
- **No cross-border data transfer** unless explicit consent is recorded
- **S3 bucket policy** denies access from non-Indian IP ranges for PII-containing buckets

### GDPR Data Residency (EU)

For compliance with the EU General Data Protection Regulation:
- **EU primary region:** eu-west-1 (Ireland) — all EU personal data at rest stays within the EU
- **EU DR region:** eu-central-1 (Frankfurt) — encrypted replication within the EU
- **Cross-border transfer controls:** Data transfers outside the EU/EEA require adequacy decisions, Standard Contractual Clauses (SCCs), or Binding Corporate Rules (BCRs)
- **S3 bucket policy** enforces EU data residency — denies replication to non-EU regions for EU tenant data
- **Right to erasure:** S3 lifecycle policies and Aurora deletion procedures support GDPR Article 17 requests
- **72-hour breach notification:** CloudWatch alarms trigger automated notification workflows to the relevant supervisory authority

### UK Data Residency

For compliance with UK GDPR and FCA/PRA requirements:
- **UK primary region:** eu-west-2 (London) — all UK personal data at rest stays in the UK
- **UK DR region:** eu-west-1 (Ireland) — permitted under UK adequacy decision for EU
- **FCA operational resilience:** Important business services mapped to infrastructure dependencies with defined impact tolerances
- **PRA SS1/23:** Model inventory and risk tiering data stored in UK region with audit trail

### Multi-Region Deployment Architecture

Tenants are assigned to a deployment region based on their jurisdiction configuration:

| Jurisdiction | Primary Region | DR Region | Data Residency Enforcement |
|-------------|---------------|-----------|---------------------------|
| India | ap-south-1 (Mumbai) | ap-south-2 (Hyderabad) | DPDP Act — data stays in India |
| EU | eu-west-1 (Ireland) | eu-central-1 (Frankfurt) | GDPR — data stays in EU/EEA |
| UK | eu-west-2 (London) | eu-west-1 (Ireland) | UK GDPR — data stays in UK (EU adequacy) |
| Multi-jurisdiction | Nearest compliant region | Cross-region encrypted replication | Per-tenant jurisdiction rules applied |

---

## 9. Observability and Monitoring

### CloudWatch Dashboard Panels

```
KavachAI Operations Dashboard
├── Pipeline Performance
│   ├── Evaluation latency (p50, p95, p99) — line chart
│   ├── Evaluations per second — area chart
│   └── Verdict distribution (ALLOW/BLOCK/ESCALATE/QUARANTINE) — pie chart
├── Threat Intelligence
│   ├── Threat score distribution — histogram
│   ├── Active kill chains — counter
│   ├── Quarantined sessions — counter
│   └── Pending escalations — counter
├── System Health
│   ├── ECS task count per service — stacked area
│   ├── CPU/memory utilization — line chart
│   ├── Aurora connections / IOPS — line chart
│   └── Redis memory / connections — line chart
├── Audit Integrity
│   ├── Hash chain verification status — traffic light
│   ├── Audit entries per minute — area chart
│   └── Evidence packages exported — counter
└── Cost
    ├── Daily cost trend — bar chart
    ├── Cost per evaluation — line chart
    └── LLM spend by model — stacked bar
```

### Alerting Rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| Pipeline latency high | p95 > 200ms for 5 min | Warning | Scale up ECS tasks |
| Pipeline latency critical | p95 > 500ms for 2 min | Critical | Page on-call + scale up |
| Error rate elevated | > 1% for 5 min | Warning | Investigate logs |
| Error rate critical | > 5% for 2 min | Critical | Page on-call + rollback |
| Audit chain broken | Any hash mismatch | Critical | Page security lead immediately |
| Quarantine spike | > 10 quarantines in 5 min | Warning | Investigate attack pattern |
| Database connections high | > 80% pool utilization | Warning | Scale Aurora ACUs |
| Redis memory high | > 80% utilization | Warning | Scale ElastiCache |
| Budget exceeded | LLM cost > 90% of monthly budget | Warning | Notify finance + throttle |
| Certificate expiry | < 30 days to expiry | Warning | ACM auto-renewal check |

### Distributed Tracing with X-Ray

Every evaluation pipeline execution is traced end-to-end:

```
Trace: evaluate_action
├── Segment: auth_stage (2ms)
├── Segment: capability_token_stage (1ms)
├── Segment: dsl_policy_stage (8ms)
│   └── Subsegment: rule_evaluation × N
├── Segment: threat_detection_stage (15ms)
│   ├── Subsegment: prompt_injection (3ms)
│   ├── Subsegment: tool_poisoning (2ms)
│   ├── Subsegment: privilege_escalation (2ms)
│   ├── Subsegment: covert_channel (3ms)
│   └── Subsegment: attack_chain (5ms)
├── Segment: audit_trail_append (12ms)
│   └── Subsegment: aurora_insert
└── Total: 45ms
```

---

## 10. Disaster Recovery and Business Continuity

### DR Strategy: Warm Standby

| Component | Primary (ap-south-1) | DR (ap-south-2) | Failover |
|-----------|---------------------|-----------------|----------|
| Compute | ECS Fargate (active) | ECS Fargate (1 task standby) | Route 53 failover, scale up DR |
| Database | Aurora writer | Aurora Global Database (read replica) | Promote replica to writer (< 1 min) |
| Cache | ElastiCache cluster | ElastiCache Global Datastore | Promote DR to primary |
| Storage | S3 (primary) | S3 Cross-Region Replication | Already replicated |
| DNS | Route 53 health check | Failover record | Automatic (< 60s) |

### Recovery Objectives

- **RTO (Recovery Time Objective):** < 15 minutes for full regional failover
- **RPO (Recovery Point Objective):** < 1 minute (Aurora Global Database replication lag)

### Backup Strategy

| Data | Backup Method | Frequency | Retention |
|------|--------------|-----------|-----------|
| Aurora database | Automated snapshots | Continuous (5-min PITR) | 35 days |
| Aurora database | Manual snapshots | Weekly | 1 year |
| S3 evidence packages | Cross-region replication | Real-time | 7 years (Object Lock) |
| Redis state | ElastiCache snapshots | Daily | 7 days (state is reconstructable) |
| Secrets | Secrets Manager versioning | On every rotation | 10 versions |
| CDK/IaC code | Git (GitLab) | Every commit | Indefinite |

---

## 11. Cost Estimation

### Sizing Tiers

| Tier | Evaluations/day | Monthly Cost | Cost/Evaluation |
|------|----------------|-------------|-----------------|
| Starter | 10,000 | ~$500 | $0.0017 |
| Growth | 100,000 | ~$800 | $0.00027 |
| Enterprise | 1,000,000 | ~$2,500 | $0.000083 |
| Scale | 10,000,000 | ~$8,000 | $0.000027 |

Cost decreases per evaluation as volume increases due to fixed costs (ALB, NAT, base Aurora ACUs) being amortized.

### Cost Optimization Roadmap

| Timeline | Action | Savings |
|----------|--------|---------|
| Month 1 | Deploy with on-demand pricing, establish baselines | Baseline |
| Month 3 | Purchase 1-year Compute Savings Plan | 30-40% on Fargate |
| Month 6 | Implement S3 Intelligent-Tiering for evidence | 40% on storage |
| Month 12 | Move to Graviton (arm64) Fargate tasks | 20% on compute |
| Month 12 | VPC endpoints for S3/ECR (eliminate NAT for those) | $50-100/month |


---

## 12. Rollout Plan

### Phase 0: Foundation (Weeks 1-2)

**Goal:** Infrastructure provisioned, CI/CD pipeline operational.

| Task | Owner | Duration |
|------|-------|----------|
| Set up AWS accounts (dev, staging, prod) with AWS Organizations | Platform | 1 day |
| Deploy CDK stacks: VPC, Aurora, ElastiCache, ECR | Platform | 2 days |
| Configure CI/CD pipeline (CodePipeline + CodeBuild) | DevOps | 2 days |
| Set up Cognito user pool and API Gateway | Security | 1 day |
| Configure CloudWatch dashboards and alarms | SRE | 1 day |
| Migrate SQLite schema to Aurora PostgreSQL | Backend | 2 days |
| Security review: IAM policies, security groups, encryption | Security | 2 days |
| Load testing with k6 (baseline performance) | QA | 1 day |

**Exit Criteria:** All services running in staging, CI/CD deploying automatically, all alarms green.

### Phase 1: Internal Pilot (Weeks 3-4)

**Goal:** KavachAI protecting internal AI agents with real traffic.

| Task | Owner | Duration |
|------|-------|----------|
| Onboard 1-2 internal AI agents (low-risk use cases) | Product | 2 days |
| Write production DSL policies for internal use cases | Security | 3 days |
| Configure tenant isolation for pilot team | Backend | 1 day |
| Monitor pipeline latency, threat detection accuracy | SRE | Ongoing |
| Tune threat detection thresholds (reduce false positives) | ML/Security | 1 week |
| SOC team training on dashboard | Security | 1 day |
| Incident response drill | Security | 1 day |

**Exit Criteria:** < 1% false positive rate, p95 latency < 100ms, SOC team comfortable with dashboard, zero data integrity issues.

### Phase 2: Limited Production (Weeks 5-8)

**Goal:** Protecting production AI agents for one business unit.

| Task | Owner | Duration |
|------|-------|----------|
| Onboard first production business unit (5-10 agents) | Product | 1 week |
| Enable MCP Proxy Gateway for production agent fleet | Platform | 2 days |
| Configure escalation workflows with SOC team | Security | 2 days |
| Enable DPDP compliance monitoring | Compliance | 1 day |
| Enable CERT-In reporting integration | Compliance | 1 day |
| Performance optimization based on production traffic | Backend | 1 week |
| Weekly security review of threat detection findings | Security | Ongoing |

**Exit Criteria:** All production agents routed through KavachAI, escalation workflow operational, compliance reports generating correctly, no production incidents caused by KavachAI.

### Phase 3: Enterprise Rollout (Weeks 9-16)

**Goal:** All AI agents across the organization protected by KavachAI.

| Task | Owner | Duration |
|------|-------|----------|
| Onboard remaining business units (phased, 1 per week) | Product | 4-6 weeks |
| Enable multi-tenant isolation per business unit | Backend | 1 week |
| Deploy DR region (ap-south-2) | Platform | 1 week |
| Conduct DR failover drill | SRE | 1 day |
| Enable LLM evaluation and red teaming for all models | ML/Security | 2 weeks |
| Enable semantic grounding for high-risk use cases | ML | 2 weeks |
| Executive compliance dashboard | Product | 1 week |
| SOC 2 Type II audit preparation | Compliance | Ongoing |

**Exit Criteria:** 100% agent coverage, DR tested, all compliance frameworks active, executive reporting operational.

### Phase 4: Optimization (Ongoing)

| Activity | Frequency |
|----------|-----------|
| Cost optimization review | Monthly |
| Threat detection model retraining | Quarterly |
| Red team exercises | Quarterly |
| DR failover drill | Quarterly |
| Security audit | Annually |
| Compliance certification renewal | Annually |
| Capacity planning review | Quarterly |

---

## 13. Operational Runbook

### Common Operations

#### Scale Up Backend (High Traffic)

```bash
# Increase desired count for backend service
aws ecs update-service \
  --cluster kavachai-prod \
  --service kavachai-backend \
  --desired-count 10

# Or update auto-scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/kavachai-prod/kavachai-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{"TargetValue":50.0,"PredefinedMetricSpecification":{"PredefinedMetricType":"ECSServiceAverageCPUUtilization"}}'
```

#### Rotate LLM API Keys

```bash
# Update secret in Secrets Manager
aws secretsmanager update-secret \
  --secret-id kavachai/prod/openai-api-key \
  --secret-string '{"api_key":"sk-new-key-here"}'

# Force ECS tasks to pick up new secret (rolling restart)
aws ecs update-service \
  --cluster kavachai-prod \
  --service kavachai-backend \
  --force-new-deployment
```

#### Export Evidence Package for Legal

```bash
# Via API
curl -X GET "https://api.kavachai.example.com/api/v1/sessions/{session_id}/evidence-package" \
  -H "Authorization: Bearer $TOKEN" \
  -o evidence-package.json

# Verify integrity
python -c "
import json, hashlib
pkg = json.load(open('evidence-package.json'))
print('Chain valid:', pkg['chain_of_custody']['hash_chain_valid'])
print('Package hash:', pkg['package_hash'])
"
```

#### Emergency: Quarantine All Sessions for a Tenant

```bash
# Block all evaluations for a tenant by updating their rate limit to 0
aws ssm put-parameter \
  --name "/kavachai/prod/tenant/{tenant_id}/rate_limit" \
  --value "0" \
  --type String \
  --overwrite

# Or revoke all agents for the tenant via API
curl -X DELETE "https://api.kavachai.example.com/api/v1/tenants/{tenant_id}/agents" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

#### Investigate Audit Chain Integrity Failure

1. Check CloudWatch alarm details for the specific session_id
2. Query Aurora for the broken chain link:
   ```sql
   SELECT entry_id, sequence_number, entry_hash, previous_entry_hash
   FROM audit_entries
   WHERE session_id = '{session_id}'
   ORDER BY sequence_number;
   ```
3. Identify the first entry where `previous_entry_hash` does not match the preceding `entry_hash`
4. Check CloudTrail for any direct database modifications around that timestamp
5. Export evidence package for the session
6. Escalate to security lead and initiate incident response

### Incident Severity Levels

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| SEV-1 | System down or data integrity breach | 15 min | Audit chain broken, all evaluations failing, data exfiltration |
| SEV-2 | Degraded performance or partial outage | 30 min | Pipeline latency > 500ms, one AZ down, high false positive rate |
| SEV-3 | Non-critical issue | 4 hours | Dashboard slow, single agent misbehaving, non-critical alarm |
| SEV-4 | Improvement opportunity | Next business day | Cost optimization, performance tuning, feature request |

---

## Summary

This production plan transforms KavachAI from a hackathon prototype into an enterprise-grade platform by leveraging AWS managed services across all six Well-Architected pillars. The phased rollout minimizes risk while the infrastructure-as-code approach ensures reproducibility and auditability. The estimated monthly cost of ~$800 for a growth-tier deployment provides strong value for an AI safety governance platform protecting enterprise agent fleets.
