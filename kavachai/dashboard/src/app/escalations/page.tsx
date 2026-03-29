"use client";

import { useState } from "react";
import { ThreatScoreBadge } from "@/components/ThreatScoreBadge";

interface EscalationItem {
  escalation_id: string;
  tool_name: string;
  agent_id: string;
  threat_score: number;
  reason: string;
  timeout_at: string;
  status: "pending" | "approved" | "rejected";
}

const DEMO_ESCALATIONS: EscalationItem[] = [
  {
    escalation_id: "esc-001",
    tool_name: "payment_process",
    agent_id: "agent-demo-001",
    threat_score: 0.65,
    reason: "Payment > ₹50,000 by non-trusted agent",
    timeout_at: new Date(Date.now() + 45000).toISOString(),
    status: "pending",
  },
  {
    escalation_id: "esc-002",
    tool_name: "external_api",
    agent_id: "agent-demo-002",
    threat_score: 0.58,
    reason: "External API call after customer data access",
    timeout_at: new Date(Date.now() + 30000).toISOString(),
    status: "pending",
  },
];

export default function EscalationPage() {
  const [escalations, setEscalations] = useState(DEMO_ESCALATIONS);

  const resolve = (id: string, decision: "approved" | "rejected") => {
    setEscalations((prev) =>
      prev.map((e) => (e.escalation_id === id ? { ...e, status: decision } : e))
    );
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Escalation Queue</h2>

      <div className="space-y-4">
        {escalations.map((esc) => (
          <div key={esc.escalation_id} className={`bg-white rounded-lg border shadow-sm p-4 ${esc.status !== "pending" ? "opacity-60" : ""}`}>
            <div className="flex items-start justify-between">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-gray-500">{esc.escalation_id}</span>
                  <ThreatScoreBadge score={esc.threat_score} />
                  {esc.status !== "pending" && (
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${esc.status === "approved" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                      {esc.status.toUpperCase()}
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-700">{esc.reason}</p>
                <div className="flex gap-4 text-xs text-gray-500">
                  <span>Tool: <span className="font-mono">{esc.tool_name}</span></span>
                  <span>Agent: <span className="font-mono">{esc.agent_id}</span></span>
                </div>
              </div>
              {esc.status === "pending" && (
                <div className="flex gap-2 shrink-0">
                  <button
                    onClick={() => resolve(esc.escalation_id, "approved")}
                    className="px-3 py-1.5 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => resolve(esc.escalation_id, "rejected")}
                    className="px-3 py-1.5 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
                  >
                    Reject
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
