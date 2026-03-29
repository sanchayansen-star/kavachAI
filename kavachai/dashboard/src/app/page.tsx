"use client";

import { useEffect, useState } from "react";
import { VerdictChip } from "@/components/VerdictChip";
import { ThreatScoreBadge } from "@/components/ThreatScoreBadge";
import type { VerdictType, DashboardEvent } from "@/types";

interface SessionRow {
  session_id: string;
  threat_score: number;
  action_count: number;
  last_verdict: VerdictType;
  last_tool: string;
  timestamp: string;
}

// Demo data for initial render
const DEMO_SESSIONS: SessionRow[] = [
  { session_id: "sess-demo-001", threat_score: 0.95, action_count: 5, last_verdict: "quarantine", last_tool: "customer_lookup", timestamp: new Date().toISOString() },
  { session_id: "sess-demo-002", threat_score: 0.62, action_count: 3, last_verdict: "escalate", last_tool: "payment_process", timestamp: new Date().toISOString() },
  { session_id: "sess-demo-003", threat_score: 0.15, action_count: 8, last_verdict: "allow", last_tool: "verify_identity", timestamp: new Date().toISOString() },
];

export default function ThreatFeedPage() {
  const [sessions, setSessions] = useState<SessionRow[]>(DEMO_SESSIONS);
  const [alerts, setAlerts] = useState<string[]>([
    "🔴 Session sess-demo-001 quarantined — prompt injection detected",
    "🔶 Escalation pending — payment_process > ₹50,000 by untrusted agent",
  ]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Threat Feed</h2>
        <span className="text-sm text-gray-500">Real-time session monitoring</span>
      </div>

      {/* Alert Panel */}
      {alerts.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4" role="alert">
          <h3 className="text-sm font-semibold text-red-800 mb-2">Active Alerts</h3>
          <ul className="space-y-1">
            {alerts.map((a, i) => (
              <li key={i} className="text-sm text-red-700">{a}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Stats Row */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Active Sessions", value: sessions.length, color: "text-blue-600" },
          { label: "Threats Detected", value: sessions.filter((s) => s.threat_score > 0.5).length, color: "text-red-600" },
          { label: "Quarantined", value: sessions.filter((s) => s.last_verdict === "quarantine").length, color: "text-purple-600" },
          { label: "Escalations", value: sessions.filter((s) => s.last_verdict === "escalate").length, color: "text-orange-600" },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg border p-4 shadow-sm">
            <p className="text-xs text-gray-500 uppercase tracking-wide">{stat.label}</p>
            <p className={`text-3xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Session Table */}
      <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Session</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Threat Score</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Actions</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Last Tool</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Verdict</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {sessions
              .sort((a, b) => b.threat_score - a.threat_score)
              .map((s) => (
                <tr key={s.session_id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-xs">{s.session_id}</td>
                  <td className="px-4 py-3"><ThreatScoreBadge score={s.threat_score} /></td>
                  <td className="px-4 py-3">{s.action_count}</td>
                  <td className="px-4 py-3 font-mono text-xs">{s.last_tool}</td>
                  <td className="px-4 py-3"><VerdictChip verdict={s.last_verdict} /></td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
