"use client";

import { ThreatScoreBadge } from "@/components/ThreatScoreBadge";

interface ModelScore {
  model_name: string;
  overall_score: number;
  sub_scores: Record<string, number>;
  passed: boolean;
}

const DEMO_SCORES: ModelScore[] = [
  { model_name: "gpt-4", overall_score: 82, sub_scores: { prompt_injection_resistance: 85, toxicity: 90, bias: 75, hallucination: 70, accuracy: 80 }, passed: true },
  { model_name: "gpt-3.5-turbo", overall_score: 71, sub_scores: { prompt_injection_resistance: 65, toxicity: 85, bias: 70, hallucination: 60, accuracy: 75 }, passed: true },
  { model_name: "claude-3-sonnet", overall_score: 88, sub_scores: { prompt_injection_resistance: 90, toxicity: 92, bias: 85, hallucination: 80, accuracy: 88 }, passed: true },
];

const DEMO_RED_TEAM = [
  { model: "gpt-4", cases_run: 150, vulnerabilities: 8, delta: -5.3, degraded: false },
  { model: "gpt-3.5-turbo", cases_run: 150, vulnerabilities: 18, delta: -12.0, degraded: true },
];

function ScoreBar({ label, value }: { label: string; value: number }) {
  const color = value >= 80 ? "bg-green-500" : value >= 60 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-40 text-gray-600 truncate">{label}</span>
      <div className="flex-1 bg-gray-200 rounded-full h-2">
        <div className={`h-2 rounded-full ${color}`} style={{ width: `${value}%` }} />
      </div>
      <span className="w-8 text-right font-bold">{value}</span>
    </div>
  );
}

export default function ModelEvalPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Model Safety Evaluation</h2>

      {/* Safety Score Overview */}
      <div className="grid grid-cols-3 gap-4">
        {DEMO_SCORES.map((m) => (
          <div key={m.model_name} className="bg-white rounded-lg border shadow-sm p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="font-semibold text-sm">{m.model_name}</span>
              <span className={`text-xs font-bold px-2 py-0.5 rounded ${m.passed ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                {m.passed ? "PASSED" : "FAILED"}
              </span>
            </div>
            <div className="text-center mb-3">
              <span className={`text-4xl font-bold ${m.overall_score >= 70 ? "text-green-600" : "text-red-600"}`}>{m.overall_score}</span>
              <span className="text-sm text-gray-400">/100</span>
            </div>
            <div className="space-y-1.5">
              {Object.entries(m.sub_scores).map(([k, v]) => (
                <ScoreBar key={k} label={k.replace(/_/g, " ")} value={v} />
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Red Team Results */}
      <div className="bg-white rounded-lg border shadow-sm p-4">
        <h3 className="text-sm font-semibold text-gray-600 mb-3">Red Team Results</h3>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Model</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Cases Run</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Vulnerabilities</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Score Delta</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {DEMO_RED_TEAM.map((r) => (
              <tr key={r.model} className="hover:bg-gray-50">
                <td className="px-4 py-2 font-mono text-xs">{r.model}</td>
                <td className="px-4 py-2">{r.cases_run}</td>
                <td className="px-4 py-2 font-bold text-red-600">{r.vulnerabilities}</td>
                <td className="px-4 py-2">
                  <span className={r.delta < -10 ? "text-red-600 font-bold" : "text-yellow-600"}>{r.delta.toFixed(1)}%</span>
                </td>
                <td className="px-4 py-2">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded ${r.degraded ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"}`}>
                    {r.degraded ? "DEGRADED" : "STABLE"}
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
