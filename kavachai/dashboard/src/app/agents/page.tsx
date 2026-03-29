"use client";

import { TrustLevelBadge } from "@/components/TrustLevelBadge";
import { ThreatScoreBadge } from "@/components/ThreatScoreBadge";
import type { TrustLevel } from "@/types";

interface AgentRow {
  agent_id: string;
  name: string;
  trust_score: number;
  trust_level: TrustLevel;
  capability_scope: string[];
  status: "active" | "revoked";
}

const DEMO_AGENTS: AgentRow[] = [
  { agent_id: "agent-001", name: "financial-assistant", trust_score: 0.85, trust_level: "trusted", capability_scope: ["verify_identity", "customer_lookup", "payment_process"], status: "active" },
  { agent_id: "agent-002", name: "support-bot", trust_score: 0.55, trust_level: "standard", capability_scope: ["customer_lookup", "send_email"], status: "active" },
  { agent_id: "agent-003", name: "compromised-agent", trust_score: 0.12, trust_level: "quarantined", capability_scope: ["customer_lookup"], status: "active" },
];

export default function AgentsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Registered Agents</h2>

      <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Agent</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Trust Score</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Trust Level</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Capabilities</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {DEMO_AGENTS.map((agent) => (
              <tr key={agent.agent_id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <p className="font-medium">{agent.name}</p>
                  <p className="font-mono text-xs text-gray-400">{agent.agent_id}</p>
                </td>
                <td className="px-4 py-3"><ThreatScoreBadge score={agent.trust_score} /></td>
                <td className="px-4 py-3"><TrustLevelBadge level={agent.trust_level} /></td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {agent.capability_scope.map((t) => (
                      <span key={t} className="bg-gray-100 text-gray-600 text-xs px-1.5 py-0.5 rounded font-mono">{t}</span>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs font-bold ${agent.status === "active" ? "text-green-600" : "text-red-600"}`}>
                    {agent.status.toUpperCase()}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
