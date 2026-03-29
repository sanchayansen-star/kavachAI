"""SQLite database manager — schema init and connection handling."""

import aiosqlite
import os

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///data/kavachai.db").replace(
    "sqlite:///", ""
)

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else "data", exist_ok=True)


async def get_db() -> aiosqlite.Connection:
    """Get an async SQLite connection."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


SCHEMA_SQL = """
-- Tenants
CREATE TABLE IF NOT EXISTS tenants (
    tenant_id       TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    api_key_hash    TEXT NOT NULL,
    llm_budget      REAL,
    rate_limit      INTEGER,
    config          TEXT NOT NULL DEFAULT '{}',
    created_at      TEXT NOT NULL
);

-- Agent registrations
CREATE TABLE IF NOT EXISTS agents (
    agent_id        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    public_key      TEXT NOT NULL,
    capability_scope TEXT NOT NULL,
    trust_score     REAL NOT NULL DEFAULT 0.5,
    trust_level     TEXT NOT NULL DEFAULT 'standard',
    tenant_id       TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    revoked         INTEGER NOT NULL DEFAULT 0,
    last_active_at  TEXT
);

-- Capability tokens
CREATE TABLE IF NOT EXISTS capability_tokens (
    token_id        TEXT PRIMARY KEY,
    agent_id        TEXT NOT NULL REFERENCES agents(agent_id),
    allowed_tools   TEXT NOT NULL,
    expires_at      TEXT NOT NULL,
    signature       TEXT NOT NULL,
    tenant_id       TEXT NOT NULL,
    revoked         INTEGER NOT NULL DEFAULT 0
);

-- Core audit trail with hash chain integrity
CREATE TABLE IF NOT EXISTS audit_entries (
    entry_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT NOT NULL,
    session_id      TEXT NOT NULL,
    tenant_id       TEXT NOT NULL,
    agent_identity_hash TEXT NOT NULL,
    action_type     TEXT NOT NULL,
    action_params_hash TEXT NOT NULL,
    action_verdict  TEXT NOT NULL,
    matched_policies TEXT,
    threat_score    REAL NOT NULL DEFAULT 0.0,
    ethics_score    REAL DEFAULT NULL,
    grounding_score REAL DEFAULT NULL,
    llm_reasoning   TEXT,
    model_name      TEXT,
    model_version   TEXT,
    llm_tokens      INTEGER,
    llm_cost        REAL,
    trust_score_before REAL,
    trust_score_after  REAL,
    previous_entry_hash TEXT NOT NULL,
    entry_hash      TEXT NOT NULL UNIQUE,
    sequence_number INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_session
    ON audit_entries(session_id, sequence_number);
CREATE INDEX IF NOT EXISTS idx_audit_tenant
    ON audit_entries(tenant_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_agent
    ON audit_entries(agent_identity_hash, timestamp);

-- Policy storage
CREATE TABLE IF NOT EXISTS policies (
    policy_id       TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    dsl_source      TEXT NOT NULL,
    ast_json        TEXT NOT NULL,
    verification_cert TEXT,
    status          TEXT NOT NULL DEFAULT 'active',
    tenant_id       TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- DFA behavioral models
CREATE TABLE IF NOT EXISTS dfa_models (
    model_id        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    states          TEXT NOT NULL,
    transitions     TEXT NOT NULL,
    tenant_id       TEXT NOT NULL
);

-- Kill chains
CREATE TABLE IF NOT EXISTS kill_chains (
    kill_chain_id   TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL,
    stages          TEXT NOT NULL,
    overall_threat  REAL NOT NULL,
    is_stac_attack  INTEGER NOT NULL DEFAULT 0,
    detected_at     TEXT NOT NULL,
    tenant_id       TEXT NOT NULL
);

-- Escalations
CREATE TABLE IF NOT EXISTS escalations (
    escalation_id   TEXT PRIMARY KEY,
    action_request  TEXT NOT NULL,
    threat_score    REAL NOT NULL,
    kill_chain_id   TEXT,
    status          TEXT NOT NULL DEFAULT 'pending',
    operator_id     TEXT,
    operator_reason TEXT,
    timeout_at      TEXT NOT NULL,
    resolved_at     TEXT,
    tenant_id       TEXT NOT NULL
);

-- LLM model evaluations
CREATE TABLE IF NOT EXISTS model_evaluations (
    evaluation_id   TEXT PRIMARY KEY,
    model_name      TEXT NOT NULL,
    model_version   TEXT NOT NULL,
    overall_score   INTEGER NOT NULL,
    sub_scores      TEXT NOT NULL,
    benchmark_id    TEXT NOT NULL,
    passed          INTEGER NOT NULL,
    evaluated_at    TEXT NOT NULL,
    tenant_id       TEXT NOT NULL
);

-- Red team runs
CREATE TABLE IF NOT EXISTS red_team_runs (
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
CREATE TABLE IF NOT EXISTS knowledge_graphs (
    graph_id        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    domain          TEXT NOT NULL,
    nodes           TEXT NOT NULL,
    edges           TEXT NOT NULL,
    source_type     TEXT NOT NULL,
    source_config   TEXT,
    tenant_id       TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- Domain ontologies
CREATE TABLE IF NOT EXISTS domain_ontologies (
    ontology_id     TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    domain          TEXT NOT NULL,
    concepts        TEXT NOT NULL,
    relationships   TEXT NOT NULL,
    tenant_id       TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- Grounding results
CREATE TABLE IF NOT EXISTS grounding_results (
    result_id       TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL,
    output_id       TEXT NOT NULL,
    grounding_score REAL NOT NULL,
    claims          TEXT NOT NULL,
    schema_valid    INTEGER NOT NULL,
    deterministic_checks TEXT NOT NULL,
    verdict         TEXT NOT NULL,
    tenant_id       TEXT NOT NULL,
    created_at      TEXT NOT NULL
);
"""


async def init_db():
    """Initialize database schema."""
    db = await get_db()
    try:
        await db.executescript(SCHEMA_SQL)
        await db.commit()
    finally:
        await db.close()
