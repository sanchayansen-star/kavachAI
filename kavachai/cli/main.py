"""kavach — KavachAI command-line interface.

Usage:
    kavach demo run              Run the 5-stage attack demo
    kavach agent create          Register a new agent
    kavach agent list            List registered agents
    kavach agent revoke          Revoke an agent
    kavach policy upload         Upload a .shield policy file
    kavach policy list           List loaded policies
    kavach policy verify         Verify a policy for consistency
    kavach evaluate              Evaluate a single action
    kavach compliance status     Show multi-jurisdiction compliance
    kavach server start          Start the KavachAI backend server
"""

import asyncio
import json
import os
import sys
import uuid

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

# Ensure project root is on path
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _run(coro):
    """Run an async coroutine from sync Click commands."""
    return asyncio.run(coro)


async def _init_db():
    from kavachai.backend.db.database import init_db
    await init_db()


# ── Shared state (lazy-loaded singletons) ──

_identity_mgr = None
_policy_engine = None
_pipeline = None


def _get_identity_mgr():
    global _identity_mgr
    if _identity_mgr is None:
        from kavachai.backend.core.identity import AgentIdentityManager
        _identity_mgr = AgentIdentityManager()
    return _identity_mgr


def _get_policy_engine():
    global _policy_engine
    if _policy_engine is None:
        from kavachai.backend.core.policy_engine import PolicyEngine
        _policy_engine = PolicyEngine()
    return _policy_engine


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        from kavachai.backend.core.pipeline import EvalPipeline
        from kavachai.backend.threat.detector import ThreatDetector
        _pipeline = EvalPipeline(
            identity_mgr=_get_identity_mgr(),
            policy_engine=_get_policy_engine(),
            threat_detector=ThreatDetector(),
        )
    return _pipeline


# ═══════════════════════════════════════════════════════════════
# Root group
# ═══════════════════════════════════════════════════════════════

@click.group()
@click.version_option(version="0.1.0", prog_name="kavach")
def cli():
    """🛡️  KavachAI — Zero Trust Safety Firewall for Agentic AI"""
    pass


# ═══════════════════════════════════════════════════════════════
# kavach demo
# ═══════════════════════════════════════════════════════════════

@cli.group()
def demo():
    """Run demo scenarios."""
    pass


@demo.command("run")
def demo_run():
    """Run the 5-stage financial services attack demo."""
    async def _run_demo():
        await _init_db()
        from kavachai.backend.demo.scenario import DemoScenario

        console.print(Panel.fit(
            "[bold cyan]KavachAI — Zero Trust Safety Firewall Demo[/]\n"
            "[dim]5-Stage Financial Services Attack Scenario[/]",
            border_style="cyan",
        ))
        console.print()

        scenario = DemoScenario()
        results = await scenario.run_all_stages()

        icons = {"allow": "✅", "block": "🛑", "flag": "⚠️", "escalate": "🔶", "quarantine": "🔴"}

        for r in results:
            icon = icons.get(r["verdict"], "❓")
            verdict_color = {
                "allow": "green", "block": "red", "flag": "yellow",
                "escalate": "dark_orange", "quarantine": "magenta",
            }.get(r["verdict"], "white")

            console.print(f"[bold]Stage {r['stage']}:[/] {r['name']}")
            console.print(f"  Tool:    [cyan]{r['tool']}[/]")
            console.print(f"  Verdict: {icon} [{verdict_color}]{r['verdict'].upper()}[/]")
            console.print(f"  Threat:  {r['threat_score']:.2f}")
            console.print(f"  Reason:  [dim]{r['reason']}[/]")
            console.print()

        blocked = sum(1 for r in results if r["verdict"] in ("block", "quarantine", "escalate"))
        console.print(Panel.fit(
            f"[bold green]{blocked}/{len(results)} attack stages detected and blocked/escalated[/]",
            border_style="green",
        ))

    _run(_run_demo())


# ═══════════════════════════════════════════════════════════════
# kavach agent
# ═══════════════════════════════════════════════════════════════

@cli.group()
def agent():
    """Manage AI agent identities."""
    pass


@agent.command("create")
@click.option("--name", "-n", required=True, help="Agent name")
@click.option("--tools", "-t", required=True, help="Comma-separated tool names")
@click.option("--tenant", default="default", help="Tenant ID")
def agent_create(name, tools, tenant):
    """Register a new agent with capability scope."""
    from kavachai.backend.models.agent import ToolScope

    mgr = _get_identity_mgr()
    tool_list = [t.strip() for t in tools.split(",")]
    identity, private_key = mgr.register_agent(name=name, capability_scope=tool_list, tenant_id=tenant)

    # Issue initial token
    token = mgr.issue_capability_token(
        agent_id=identity.agent_id,
        allowed_tools=[ToolScope(tool_name=t) for t in tool_list],
    )

    console.print(Panel.fit(
        f"[bold green]Agent registered successfully[/]\n\n"
        f"[bold]Agent ID:[/]    {identity.agent_id}\n"
        f"[bold]Name:[/]        {name}\n"
        f"[bold]Tools:[/]       {', '.join(tool_list)}\n"
        f"[bold]Trust:[/]       {identity.trust_score} ({identity.trust_level.value})\n"
        f"[bold]Token ID:[/]    {token.token_id}\n"
        f"[bold]Public Key:[/]  {identity.public_key[:32]}...\n"
        f"[bold]Private Key:[/] {private_key[:32]}... [dim](save this!)[/]",
        title="🤖 New Agent",
        border_style="green",
    ))


@agent.command("list")
def agent_list():
    """List all registered agents."""
    mgr = _get_identity_mgr()
    agents = list(mgr._agents.values())

    if not agents:
        console.print("[dim]No agents registered. Use 'kavach agent create' to register one.[/]")
        return

    table = Table(title="Registered Agents")
    table.add_column("Agent ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Trust", justify="right")
    table.add_column("Level")
    table.add_column("Tools")
    table.add_column("Status")

    for a in agents:
        level_color = {"trusted": "green", "standard": "blue", "restricted": "yellow", "quarantined": "red"}.get(a.trust_level.value, "white")
        table.add_row(
            a.agent_id[:12] + "...",
            a.name,
            f"{a.trust_score:.2f}",
            f"[{level_color}]{a.trust_level.value.upper()}[/]",
            ", ".join(a.capability_scope[:3]) + ("..." if len(a.capability_scope) > 3 else ""),
            "[red]REVOKED[/]" if a.revoked else "[green]ACTIVE[/]",
        )

    console.print(table)


@agent.command("revoke")
@click.argument("agent_id")
def agent_revoke(agent_id):
    """Revoke an agent identity."""
    mgr = _get_identity_mgr()
    if mgr.revoke_agent(agent_id):
        console.print(f"[bold red]Agent {agent_id} revoked.[/]")
    else:
        console.print(f"[red]Agent not found: {agent_id}[/]")


# ═══════════════════════════════════════════════════════════════
# kavach policy
# ═══════════════════════════════════════════════════════════════

@cli.group()
def policy():
    """Manage safety policies."""
    pass


@policy.command("upload")
@click.argument("filepath", type=click.Path(exists=True))
def policy_upload(filepath):
    """Upload a .shield policy file."""
    from kavachai.backend.core.dsl_parser import parse_dsl, DSLParseError

    with open(filepath) as f:
        source = f.read()

    try:
        ast = parse_dsl(source)
    except DSLParseError as e:
        console.print(f"[bold red]Parse error at line {e.line}, col {e.column}:[/] {e}")
        raise SystemExit(1)

    engine = _get_policy_engine()
    engine.load_policy(ast)

    console.print(Panel.fit(
        f"[bold green]Policy loaded successfully[/]\n\n"
        f"[bold]Policy ID:[/]  {ast.policy_id}\n"
        f"[bold]Name:[/]       {ast.name}\n"
        f"[bold]Version:[/]    {ast.version}\n"
        f"[bold]Rules:[/]      {len(ast.rules)}\n"
        f"[bold]Workflows:[/]  {len(ast.workflows)}\n"
        f"[bold]Ethics:[/]     {len(ast.ethics_rules)}",
        title="📜 Policy Loaded",
        border_style="blue",
    ))


@policy.command("list")
def policy_list():
    """List loaded policies."""
    engine = _get_policy_engine()
    policies = engine.get_policies()

    if not policies:
        console.print("[dim]No policies loaded. Use 'kavach policy upload <file>' to load one.[/]")
        return

    table = Table(title="Loaded Policies")
    table.add_column("Policy ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Version")
    table.add_column("Rules", justify="right")
    table.add_column("Workflows", justify="right")

    for p in policies:
        table.add_row(p.policy_id[:12] + "...", p.name, p.version, str(len(p.rules)), str(len(p.workflows)))

    console.print(table)


@policy.command("verify")
@click.argument("filepath", type=click.Path(exists=True))
def policy_verify(filepath):
    """Verify a policy file for consistency and completeness."""
    from kavachai.backend.core.dsl_parser import parse_dsl, DSLParseError
    from kavachai.backend.core.formal_verifier import FormalPolicyVerifier

    with open(filepath) as f:
        source = f.read()

    try:
        ast = parse_dsl(source)
    except DSLParseError as e:
        console.print(f"[bold red]Parse error:[/] {e}")
        raise SystemExit(1)

    verifier = FormalPolicyVerifier()
    cert = verifier.verify(ast)

    status_color = "green" if cert.consistent else "red"
    console.print(Panel.fit(
        f"[bold {status_color}]{'PASSED' if cert.consistent else 'FAILED'}[/]\n\n"
        f"[bold]Consistent:[/]  {'✅ Yes' if cert.consistent else '❌ No'}\n"
        f"[bold]Complete:[/]    {'✅ Yes' if cert.complete else '⚠️  Unknown (no tool list provided)'}\n"
        f"[bold]Conflicts:[/]   {len(cert.conflicts)}\n"
        f"[bold]Properties:[/]  {', '.join(cert.properties_proven) or 'none'}\n"
        f"[bold]Hash:[/]        {cert.policy_hash[:16]}...",
        title="🔍 Verification Result",
        border_style=status_color,
    ))

    for conflict in cert.conflicts:
        console.print(f"  [red]⚠ {conflict}[/]")


# ═══════════════════════════════════════════════════════════════
# kavach evaluate
# ═══════════════════════════════════════════════════════════════

@cli.command("evaluate")
@click.option("--agent-id", "-a", required=True, help="Agent ID")
@click.option("--tool", "-t", required=True, help="Tool name to evaluate")
@click.option("--params", "-p", default="{}", help="JSON parameters")
@click.option("--session", "-s", default=None, help="Session ID (auto-generated if omitted)")
def evaluate(agent_id, tool, params, session):
    """Evaluate a single action through the pipeline."""
    from kavachai.backend.models.action import ActionRequest

    async def _eval():
        await _init_db()
        pipeline = _get_pipeline()

        request = ActionRequest(
            request_id=str(uuid.uuid4()),
            agent_id=agent_id,
            session_id=session or str(uuid.uuid4()),
            tool_name=tool,
            parameters=json.loads(params),
        )

        verdict = await pipeline.evaluate(request)

        icons = {"allow": "✅", "block": "🛑", "flag": "⚠️", "escalate": "🔶", "quarantine": "🔴"}
        icon = icons.get(verdict.verdict.value, "❓")
        color = {"allow": "green", "block": "red", "flag": "yellow", "escalate": "dark_orange", "quarantine": "magenta"}.get(verdict.verdict.value, "white")

        console.print(Panel.fit(
            f"{icon} [bold {color}]{verdict.verdict.value.upper()}[/]\n\n"
            f"[bold]Tool:[/]      {tool}\n"
            f"[bold]Agent:[/]     {agent_id[:16]}...\n"
            f"[bold]Threat:[/]    {verdict.threat_score:.2f}\n"
            f"[bold]Policies:[/]  {', '.join(verdict.matched_policies) or 'none'}\n"
            f"[bold]Reason:[/]    {verdict.reason}",
            title="⚡ Evaluation Result",
            border_style=color,
        ))

    _run(_eval())


# ═══════════════════════════════════════════════════════════════
# kavach compliance
# ═══════════════════════════════════════════════════════════════

@cli.group()
def compliance():
    """View compliance status across jurisdictions."""
    pass


@compliance.command("status")
def compliance_status():
    """Show multi-jurisdiction compliance status."""
    from kavachai.backend.compliance.dpdp_engine import DPDPComplianceEngine
    from kavachai.backend.compliance.gdpr_engine import GDPRComplianceEngine
    from kavachai.backend.compliance.fca_pra_engine import FinancialRegulatoryEngine
    from kavachai.backend.compliance.seven_sutras import SevenSutrasMapper

    # DPDP
    dpdp = DPDPComplianceEngine().get_status()
    console.print(Panel.fit(
        f"[bold]Overall:[/]       {'✅ Compliant' if dpdp.overall_compliant else '❌ Non-compliant'}\n"
        f"[bold]Consent:[/]       {dpdp.consent_coverage:.0%}\n"
        f"[bold]PII Masking:[/]   {dpdp.pii_masking_rate:.0%}\n"
        f"[bold]Localization:[/]  {'✅' if dpdp.localization_compliant else '❌'}",
        title="🇮🇳 DPDP Act 2023 (India)",
        border_style="yellow",
    ))

    # GDPR
    gdpr = GDPRComplianceEngine().get_status()
    console.print(Panel.fit(
        f"[bold]Overall:[/]       {'✅ Compliant' if gdpr.overall_compliant else '❌ Non-compliant'}\n"
        f"[bold]Lawful Basis:[/]  {gdpr.lawful_basis_coverage:.0%}\n"
        f"[bold]Erasure Reqs:[/]  {gdpr.erasure_requests_pending} pending\n"
        f"[bold]Breaches:[/]      {gdpr.breach_notifications_overdue} overdue\n"
        f"[bold]DPO:[/]           {'✅ Appointed' if gdpr.dpo_appointed else '❌ Not appointed'}",
        title="🇪🇺 GDPR (EU)",
        border_style="blue",
    ))

    # FCA/PRA
    fca = FinancialRegulatoryEngine().get_status()
    console.print(Panel.fit(
        f"[bold]Overall:[/]       {'✅ Compliant' if fca.overall_compliant else '❌ Non-compliant'}\n"
        f"[bold]Consumer Duty:[/] {fca.consumer_duty_status}\n"
        f"[bold]Model Risk:[/]    {fca.model_risk_tier} ({fca.model_validation_status})\n"
        f"[bold]SM&CR:[/]         {fca.senior_managers_assigned} managers, {fca.ai_systems_covered} systems\n"
        f"[bold]DORA:[/]          {fca.dora_ict_risk_status}",
        title="🇬🇧 FCA / PRA (UK)",
        border_style="magenta",
    ))

    # Seven Sutras
    sutras = SevenSutrasMapper().compute_scores(
        has_audit_trail=True, has_pii_masking=True, has_ethics_engine=True,
        has_threat_detection=True, has_dpdp_compliance=True,
    )
    scores = sutras.to_dict()
    bars = ""
    for name, score in scores.items():
        filled = int(score / 5)
        empty = 20 - filled
        color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
        bars += f"  {name.replace('_', ' '):>15s}  [{color}]{'█' * filled}{'░' * empty}[/] {score}%\n"

    console.print(Panel.fit(bars.rstrip(), title="🇮🇳 India AI Seven Sutras", border_style="yellow"))


# ═══════════════════════════════════════════════════════════════
# kavach server
# ═══════════════════════════════════════════════════════════════

@cli.group()
def server():
    """Manage the KavachAI backend server."""
    pass


@server.command("start")
@click.option("--port", "-p", default=8000, help="Port number")
@click.option("--host", "-h", default="0.0.0.0", help="Host address")
def server_start(port, host):
    """Start the KavachAI backend server."""
    console.print(f"[bold cyan]Starting KavachAI server on {host}:{port}...[/]")
    console.print(f"  API:       http://localhost:{port}")
    console.print(f"  Swagger:   http://localhost:{port}/docs")
    console.print(f"  Health:    http://localhost:{port}/health")
    console.print()

    import uvicorn
    uvicorn.run("kavachai.backend.main:app", host=host, port=port, reload=True)


# ═══════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    cli()
