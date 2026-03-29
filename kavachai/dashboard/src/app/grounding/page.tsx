"use client";

import { ThreatScoreBadge } from "@/components/ThreatScoreBadge";

interface GroundingRow {
  session_id: string;
  grounding_score: number;
  total_claims: number;
  grounded_claims: number;
  ungrounded_claims: number;
  verdict: "GROUNDED" | "INSUFFICIENTLY_GROUNDED" | "BLOCKED";
}

const DEMO_GROUNDING: GroundingRow[] = [
  { session_id: "sess-001", grounding_score: 0.92, total_claims: 12, grounded_claims: 11, ungrounded_claims: 1, verdict: "GROUNDED" },
  { session_id: "sess-002", grounding_score: 0.55, total_claims: 9, grounded_claims: 5, ungrounded_claims: 4, verdict: "INSUFFICIENTLY_GROUNDED" },
  { session_id: "sess-003", grounding_score: 0.0, total_claims: 3, grounded_claims: 0, ungrounded_claims: 3, verdict: "BLOCKED" },
];

const DEMO_CLAIMS = [
  { claim: "Customer account balance is ₹1,50,000", source: "knowledge_graph: acc-001", grounded: true },
  { claim: "KYC verification was completed on 2026-01-15", source: "tool_response: verify_identity", grounded: true },
  { claim: "Customer has 3 active loans", source: null, grounded: false },
  { claim: "Transaction limit is ₹1,00,000", source: "ontology: payment.constraints", grounded: true },
];

const verdictColors = {
  GROUNDED: "bg-green-100 text-green-800",
  INSUFFICIENTLY_GROUNDED: "bg-yellow-100 text-yellow-800",
  BLOCKED: "bg-red-100 text-red-800",
};

export default function GroundingPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Grounding Reports</h2>

      {/* Session Grounding Table */}
      <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Session</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Score</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Claims</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Ungrounded</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Verdict</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {DEMO_GROUNDING.map((r) => (
              <tr key={r.session_id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-mono text-xs">{r.session_id}</td>
                <td className="px-4 py-3"><ThreatScoreBadge score={r.grounding_score} /></td>
                <td className="px-4 py-3">{r.grounded_claims}/{r.total_claims}</td>
                <td className="px-4 py-3 font-bold text-red-600">{r.ungrounded_claims}</td>
                <td className="px-4 py-3">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded ${verdictColors[r.verdict]}`}>{r.verdict}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Claim Verification Detail */}
      <div className="bg-white rounded-lg border shadow-sm p-4">
        <h3 className="text-sm font-semibold text-gray-600 mb-3">Claim Verification (sess-001)</h3>
        <div className="space-y-2">
          {DEMO_CLAIMS.map((c, i) => (
            <div key={i} className={`p-3 rounded border text-sm ${c.grounded ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"}`}>
              <div className="flex items-start justify-between">
                <p className={c.grounded ? "text-green-900" : "text-red-900"}>{c.claim}</p>
                <span className={`text-xs font-bold shrink-0 ml-2 ${c.grounded ? "text-green-600" : "text-red-600"}`}>
                  {c.grounded ? "✓ GROUNDED" : "✗ UNGROUNDED"}
                </span>
              </div>
              {c.source && <p className="text-xs text-gray-500 mt-1">Source: {c.source}</p>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
