"use client";

import type { SevenSutrasScores } from "@/types";

const DEMO_DPDP = {
  overall_status: "compliant",
  consent_coverage: 0.95,
  localization_compliance: true,
  pii_masking_rate: 0.98,
};

const DEMO_SUTRAS: SevenSutrasScores = {
  trust: 90,
  people_first: 90,
  innovation: 40,
  fairness: 85,
  accountability: 70,
  understandable: 40,
  safety: 95,
};

function ProgressBar({ value, max = 100, color }: { value: number; max?: number; color: string }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="w-full bg-gray-200 rounded-full h-2.5">
      <div className={`h-2.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

export default function CompliancePage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Compliance Posture</h2>

      {/* DPDP Status */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-sm font-semibold text-gray-600 mb-4">DPDP Act 2023 Status</h3>
        <div className="grid grid-cols-4 gap-6">
          <div>
            <p className="text-xs text-gray-500 uppercase">Overall</p>
            <span className={`inline-block mt-1 px-2 py-0.5 rounded text-xs font-bold ${DEMO_DPDP.overall_status === "compliant" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
              {DEMO_DPDP.overall_status.toUpperCase()}
            </span>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase mb-1">Consent Coverage</p>
            <ProgressBar value={DEMO_DPDP.consent_coverage * 100} color="bg-blue-500" />
            <p className="text-xs text-gray-600 mt-1">{(DEMO_DPDP.consent_coverage * 100).toFixed(0)}%</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase mb-1">PII Masking Rate</p>
            <ProgressBar value={DEMO_DPDP.pii_masking_rate * 100} color="bg-green-500" />
            <p className="text-xs text-gray-600 mt-1">{(DEMO_DPDP.pii_masking_rate * 100).toFixed(0)}%</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Data Localization</p>
            <span className="inline-block mt-1 px-2 py-0.5 rounded text-xs font-bold bg-green-100 text-green-800">
              {DEMO_DPDP.localization_compliance ? "COMPLIANT" : "NON-COMPLIANT"}
            </span>
          </div>
        </div>
      </div>

      {/* Seven Sutras Radar */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="text-sm font-semibold text-gray-600 mb-4">India AI Seven Sutras</h3>
        <div className="space-y-3">
          {Object.entries(DEMO_SUTRAS).map(([key, value]) => (
            <div key={key} className="flex items-center gap-3">
              <span className="w-32 text-sm text-gray-600 capitalize">{key.replace("_", " ")}</span>
              <div className="flex-1">
                <ProgressBar
                  value={value}
                  color={value >= 80 ? "bg-green-500" : value >= 50 ? "bg-yellow-500" : "bg-red-500"}
                />
              </div>
              <span className="w-10 text-right text-sm font-bold text-gray-700">{value}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
