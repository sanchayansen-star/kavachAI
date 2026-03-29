"use client";

import { useState } from "react";
import { VerdictChip } from "@/components/VerdictChip";
import { ThreatScoreBadge } from "@/components/ThreatScoreBadge";
import { HashChainIndicator } from "@/components/HashChainIndicator";
import type { VerdictType } from "@/types";

interface AuditStep {
  seq: number;
  tool: string;
  verdict: VerdictType;
  threat_score: number;
  timestamp: string;
  reasoning: { llm: string | null; policy: string; user_facing: string };
  hash: string;
}

const DEMO_TRAIL: AuditStep[] = [
  { seq: 1, tool: "customer_lookup", verdict: "quarantine", threat_score: 0.95, timestamp: "10:01:00", reasoning: { llm: null, policy: "Prompt injection detected (score 0.95)", user_facing: "Action quarantined due to critical safety concerns." }, hash: "a3f2...c891" },
  { seq: 2, tool: "send_email", verdict: "quarantine", threat_score: 0.0, timestamp: "10:01:30", reasoning: { llm: null, policy: "Rule prevent_aadhaar_exfiltration matched", user_facing: "Action quarantined — Aadhaar exfiltration attempt blocked." }, hash: "b7e1...d452" },
  { seq: 3, tool: "admin_panel", verdict: "block", threat_score: 0.0, timestamp: "10:02:00", reasoning: { llm: null, policy: "Tool not in capability scope", user_facing: "Action blocked — insufficient permissions." }, hash: "c9d3...e563" },
  { seq: 4, tool: "send_email", verdict: "quarantine", threat_score: 0.0, timestamp: "10:02:30", reasoning: { llm: null, policy: "Rule prevent_aadhaar_exfiltration matched", user_facing: "Action quarantined — covert data channel detected." }, hash: "d1a4...f674" },
  { seq: 5, tool: "payment_process", verdict: "escalate", threat_score: 0.0, timestamp: "10:03:00", reasoning: { llm: null, policy: "Rule block_unauthorized_payment matched", user_facing: "Action escalated — requires human review." }, hash: "e2b5...0785" },
];

export default function ForensicPage() {
  const [selected, setSelected] = useState<AuditStep | null>(DEMO_TRAIL[0]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Forensic Investigation</h2>
        <HashChainIndicator valid={true} />
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Timeline */}
        <div className="col-span-1 bg-white rounded-lg border shadow-sm p-4">
          <h3 className="text-sm font-semibold text-gray-600 mb-3">Action Timeline</h3>
          <div className="space-y-2">
            {DEMO_TRAIL.map((step) => (
              <button
                key={step.seq}
                onClick={() => setSelected(step)}
                className={`w-full text-left p-2 rounded text-sm transition-colors ${selected?.seq === step.seq ? "bg-kavach-50 border border-kavach-500" : "hover:bg-gray-50"}`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-gray-500">#{step.seq} {step.timestamp}</span>
                  <VerdictChip verdict={step.verdict} />
                </div>
                <p className="font-mono text-xs mt-1">{step.tool}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Detail Panel */}
        <div className="col-span-2 bg-white rounded-lg border shadow-sm p-4">
          {selected ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <span className="text-lg font-bold">Step #{selected.seq}</span>
                <VerdictChip verdict={selected.verdict} />
                <ThreatScoreBadge score={selected.threat_score} />
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-xs text-gray-500 uppercase">Tool</p>
                  <p className="font-mono">{selected.tool}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase">Hash</p>
                  <p className="font-mono text-xs">{selected.hash}</p>
                </div>
              </div>

              {/* 3-Layer Reasoning */}
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-gray-600">Decision Explanation</h4>

                {selected.reasoning.llm && (
                  <div className="bg-blue-50 rounded p-3">
                    <p className="text-xs font-semibold text-blue-700 mb-1">LLM Reasoning</p>
                    <p className="text-sm text-blue-900">{selected.reasoning.llm}</p>
                  </div>
                )}

                <div className="bg-gray-50 rounded p-3">
                  <p className="text-xs font-semibold text-gray-600 mb-1">Policy Evaluation</p>
                  <p className="text-sm text-gray-800">{selected.reasoning.policy}</p>
                </div>

                <div className="bg-green-50 rounded p-3">
                  <p className="text-xs font-semibold text-green-700 mb-1">User-Facing Summary</p>
                  <p className="text-sm text-green-900">{selected.reasoning.user_facing}</p>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-400 text-sm">Select an action from the timeline</p>
          )}
        </div>
      </div>
    </div>
  );
}
