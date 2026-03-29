"use client";

import { ThreatScoreBadge } from "@/components/ThreatScoreBadge";

const DEMO_KILL_CHAIN = {
  kill_chain_id: "kc-demo-001",
  session_id: "sess-demo-001",
  overall_threat_score: 0.92,
  is_stac_attack: true,
  stages: [
    { stage_number: 1, category: "reconnaissance", description: "customer_lookup with injected prompt", threat_score: 0.95, timestamp: "2026-03-29T10:01:00Z" },
    { stage_number: 2, category: "exfiltration", description: "send_email with Aadhaar data", threat_score: 0.88, timestamp: "2026-03-29T10:01:30Z" },
    { stage_number: 3, category: "exploitation", description: "admin_panel privilege escalation", threat_score: 0.8, timestamp: "2026-03-29T10:02:00Z" },
    { stage_number: 4, category: "exfiltration", description: "send_email with base64 encoded data", threat_score: 0.7, timestamp: "2026-03-29T10:02:30Z" },
    { stage_number: 5, category: "exploitation", description: "payment_process unauthorized transfer", threat_score: 0.65, timestamp: "2026-03-29T10:03:00Z" },
  ],
};

const categoryColors: Record<string, string> = {
  reconnaissance: "bg-blue-500",
  weaponization: "bg-purple-500",
  delivery: "bg-yellow-500",
  exploitation: "bg-red-500",
  exfiltration: "bg-orange-500",
  c2: "bg-gray-700",
};

export default function KillChainPage() {
  const chain = DEMO_KILL_CHAIN;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Kill Chain Analysis</h2>
        {chain.is_stac_attack && (
          <span className="bg-red-100 text-red-800 text-xs font-bold px-3 py-1 rounded-full">
            ⚠️ STAC Attack Detected
          </span>
        )}
      </div>

      {/* Overview */}
      <div className="bg-white rounded-lg border p-4 shadow-sm flex items-center gap-6">
        <div>
          <p className="text-xs text-gray-500 uppercase">Session</p>
          <p className="font-mono text-sm">{chain.session_id}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase">Overall Threat</p>
          <ThreatScoreBadge score={chain.overall_threat_score} />
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase">Stages</p>
          <p className="text-lg font-bold">{chain.stages.length}</p>
        </div>
      </div>

      {/* Kill Chain Graph — directed timeline */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-sm font-semibold text-gray-600 mb-4">Attack Progression</h3>
        <div className="flex items-start gap-2 overflow-x-auto pb-4">
          {chain.stages.map((stage, i) => (
            <div key={stage.stage_number} className="flex items-center">
              <div className="flex flex-col items-center min-w-[140px]">
                <div className={`w-10 h-10 rounded-full ${categoryColors[stage.category] || "bg-gray-400"} flex items-center justify-center text-white font-bold text-sm`}>
                  {stage.stage_number}
                </div>
                <div className="mt-2 text-center">
                  <p className="text-xs font-semibold text-gray-700 capitalize">{stage.category}</p>
                  <p className="text-xs text-gray-500 mt-0.5 max-w-[130px]">{stage.description}</p>
                  <div className="mt-1">
                    <ThreatScoreBadge score={stage.threat_score} />
                  </div>
                </div>
              </div>
              {i < chain.stages.length - 1 && (
                <div className="w-8 h-0.5 bg-gray-300 mt-5 shrink-0" />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
