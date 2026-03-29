"use client";

interface ModelHealth {
  model: string;
  latency_p95: number;
  error_rate: number;
  refusal_rate: number;
  status: "healthy" | "warning" | "critical";
}

const DEMO_USAGE = {
  total_tokens: 1_245_800,
  total_cost: 18.67,
  budget_remaining: 81.33,
  budget_total: 100,
};

const DEMO_HEALTH: ModelHealth[] = [
  { model: "gpt-4", latency_p95: 1200, error_rate: 0.02, refusal_rate: 0.01, status: "healthy" },
  { model: "gpt-3.5-turbo", latency_p95: 450, error_rate: 0.01, refusal_rate: 0.005, status: "healthy" },
  { model: "claude-3-sonnet", latency_p95: 2100, error_rate: 0.08, refusal_rate: 0.03, status: "warning" },
];

const statusColors = { healthy: "bg-green-500", warning: "bg-yellow-500", critical: "bg-red-500" };

export default function LLMUsagePage() {
  const budgetPct = ((DEMO_USAGE.total_cost / DEMO_USAGE.budget_total) * 100).toFixed(0);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">LLM Usage & Cost</h2>

      {/* Cost Overview */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4 shadow-sm">
          <p className="text-xs text-gray-500 uppercase">Total Tokens</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">{DEMO_USAGE.total_tokens.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg border p-4 shadow-sm">
          <p className="text-xs text-gray-500 uppercase">Total Cost</p>
          <p className="text-2xl font-bold text-green-600 mt-1">${DEMO_USAGE.total_cost.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-lg border p-4 shadow-sm">
          <p className="text-xs text-gray-500 uppercase">Budget Remaining</p>
          <p className="text-2xl font-bold text-gray-700 mt-1">${DEMO_USAGE.budget_remaining.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-lg border p-4 shadow-sm">
          <p className="text-xs text-gray-500 uppercase">Budget Used</p>
          <div className="mt-2">
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div className="bg-blue-500 h-3 rounded-full" style={{ width: `${budgetPct}%` }} />
            </div>
            <p className="text-xs text-gray-600 mt-1">{budgetPct}%</p>
          </div>
        </div>
      </div>

      {/* Model Health */}
      <div className="bg-white rounded-lg border shadow-sm p-4">
        <h3 className="text-sm font-semibold text-gray-600 mb-3">Model Health</h3>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Model</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Latency (p95)</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Error Rate</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Refusal Rate</th>
              <th className="text-left px-4 py-2 font-medium text-gray-600">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {DEMO_HEALTH.map((m) => (
              <tr key={m.model} className="hover:bg-gray-50">
                <td className="px-4 py-2 font-mono text-xs">{m.model}</td>
                <td className="px-4 py-2">{m.latency_p95}ms</td>
                <td className="px-4 py-2">{(m.error_rate * 100).toFixed(1)}%</td>
                <td className="px-4 py-2">{(m.refusal_rate * 100).toFixed(1)}%</td>
                <td className="px-4 py-2">
                  <span className="flex items-center gap-1.5">
                    <span className={`w-2.5 h-2.5 rounded-full ${statusColors[m.status]}`} />
                    <span className="text-xs font-medium capitalize">{m.status}</span>
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
