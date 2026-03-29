"""Launch script for the KavachAI demo scenario."""

import asyncio
import json
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from kavachai.backend.demo.scenario import DemoScenario


async def main():
    # Initialize database
    from kavachai.backend.db.database import init_db
    await init_db()

    print("=" * 70)
    print("  KavachAI — Zero Trust Safety Firewall Demo")
    print("  5-Stage Financial Services Attack Scenario")
    print("=" * 70)
    print()

    scenario = DemoScenario()
    results = await scenario.run_all_stages()

    for r in results:
        icon = {"allow": "✅", "block": "🛑", "flag": "⚠️", "escalate": "🔶", "quarantine": "🔴"}.get(r["verdict"], "❓")
        print(f"Stage {r['stage']}: {r['name']}")
        print(f"  Tool:    {r['tool']}")
        print(f"  Verdict: {icon} {r['verdict'].upper()}")
        print(f"  Threat:  {r['threat_score']:.2f}")
        print(f"  Reason:  {r['reason']}")
        print()

    # Summary
    blocked = sum(1 for r in results if r["verdict"] in ("block", "quarantine", "escalate"))
    print(f"Summary: {blocked}/{len(results)} attack stages detected and blocked/escalated")
    print()


if __name__ == "__main__":
    asyncio.run(main())
