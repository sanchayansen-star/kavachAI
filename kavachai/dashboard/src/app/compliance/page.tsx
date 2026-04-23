"use client";

import type { SevenSutrasScores } from "@/types";

// --- Demo data ---

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

const DEMO_GDPR = {
  overall_compliant: true,
  lawful_basis_coverage: 0.92,
  erasure_requests_pending: 1,
  erasure_requests_completed: 12,
  data_portability_supported: true,
  breach_notifications_pending: 0,
  breach_notifications_overdue: 0,
  dpia_status: "completed",
  cross_border_transfers_compliant: 3,
  cross_border_transfers_total: 3,
  dpo_appointed: true,
};

const DEMO_FCA_PRA = {
  overall_compliant: false,
  fca_consumer_duty: {
    status: "partially_compliant",
    outcomes_monitored: true,
    treating_customers_fairly: true,
    operational_resilience_tested: false,
  },
  pra_ss1_23: {
    model_risk_tier: "tier_2",
    model_validation_status: "validation_in_progress",
    model_inventory_complete: true,
    ongoing_monitoring_active: true,
    model_documentation_complete: false,
  },
  smcr: {
    accountability_mapped: true,
    senior_managers_assigned: 3,
    ai_systems_covered: 5,
  },
  dora: {
    ict_risk_status: "partial",
    incident_reporting_ready: true,
    third_party_risk_assessed: false,
  },
};

// --- Components ---

function ProgressBar({ value, max = 100, color }: { value: number; max?: number; color: string }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="w-full bg-gray-200 rounded-full h-2.5">
      <div className={`h-2.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

function StatusBadge({ status, positive }: { status: string; positive?: boolean }) {
  const isGood = positive ?? (status === "compliant" || status === "completed" || status === "true");
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${isGood ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}`}>
      {status.toUpperCase().replace("_", " ")}
    </span>
  );
}

function BoolBadge({ value, trueLabel = "YES", falseLabel = "NO" }: { value: boolean; trueLabel?: string; falseLabel?: string }) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${value ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
      {value ? trueLabel : falseLabel}
    </span>
  );
}

export default function CompliancePage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-800">Compliance Posture</h2>
        <p className="text-sm text-gray-500 mt-1">Multi-jurisdiction AI governance — India, EU, and UK</p>
      </div>

      {/* DPDP Status (India) */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <h3 className="text-sm font-semibold text-gray-600">DPDP Act 2023 Status</h3>
          <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded">India</span>
        </div>
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

      {/* GDPR Status (EU) */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <h3 className="text-sm font-semibold text-gray-600">GDPR Status</h3>
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">EU</span>
        </div>
        <div className="grid grid-cols-4 gap-6 mb-4">
          <div>
            <p className="text-xs text-gray-500 uppercase">Overall</p>
            <span className={`inline-block mt-1 px-2 py-0.5 rounded text-xs font-bold ${DEMO_GDPR.overall_compliant ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
              {DEMO_GDPR.overall_compliant ? "COMPLIANT" : "NON-COMPLIANT"}
            </span>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase mb-1">Lawful Basis Coverage</p>
            <ProgressBar value={DEMO_GDPR.lawful_basis_coverage * 100} color="bg-blue-500" />
            <p className="text-xs text-gray-600 mt-1">{(DEMO_GDPR.lawful_basis_coverage * 100).toFixed(0)}%</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">DPIA Status</p>
            <StatusBadge status={DEMO_GDPR.dpia_status} />
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">DPO Appointed</p>
            <BoolBadge value={DEMO_GDPR.dpo_appointed} />
          </div>
        </div>
        <div className="grid grid-cols-4 gap-6">
          <div>
            <p className="text-xs text-gray-500 uppercase">Erasure Requests</p>
            <p className="text-sm text-gray-700 mt-1">
              <span className="font-bold">{DEMO_GDPR.erasure_requests_pending}</span> pending · <span className="font-bold">{DEMO_GDPR.erasure_requests_completed}</span> completed
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Breach Notifications</p>
            <p className="text-sm text-gray-700 mt-1">
              <span className="font-bold">{DEMO_GDPR.breach_notifications_pending}</span> pending · <span className={`font-bold ${DEMO_GDPR.breach_notifications_overdue > 0 ? "text-red-600" : "text-green-600"}`}>{DEMO_GDPR.breach_notifications_overdue}</span> overdue
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Cross-Border Transfers</p>
            <p className="text-sm text-gray-700 mt-1">
              <span className="font-bold">{DEMO_GDPR.cross_border_transfers_compliant}</span> / {DEMO_GDPR.cross_border_transfers_total} compliant
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Data Portability</p>
            <BoolBadge value={DEMO_GDPR.data_portability_supported} trueLabel="SUPPORTED" falseLabel="NOT SUPPORTED" />
          </div>
        </div>
      </div>

      {/* UK FCA / PRA Status */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <h3 className="text-sm font-semibold text-gray-600">UK FCA / PRA Status</h3>
          <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">UK</span>
        </div>

        {/* FCA Consumer Duty */}
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-500 uppercase mb-2">FCA Consumer Duty</p>
          <div className="grid grid-cols-4 gap-6">
            <div>
              <p className="text-xs text-gray-500">Status</p>
              <StatusBadge status={DEMO_FCA_PRA.fca_consumer_duty.status} />
            </div>
            <div>
              <p className="text-xs text-gray-500">Outcomes Monitored</p>
              <BoolBadge value={DEMO_FCA_PRA.fca_consumer_duty.outcomes_monitored} />
            </div>
            <div>
              <p className="text-xs text-gray-500">Treating Customers Fairly</p>
              <BoolBadge value={DEMO_FCA_PRA.fca_consumer_duty.treating_customers_fairly} />
            </div>
            <div>
              <p className="text-xs text-gray-500">Operational Resilience</p>
              <BoolBadge value={DEMO_FCA_PRA.fca_consumer_duty.operational_resilience_tested} trueLabel="TESTED" falseLabel="NOT TESTED" />
            </div>
          </div>
        </div>

        {/* PRA SS1/23 */}
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-500 uppercase mb-2">PRA SS1/23 Model Risk</p>
          <div className="grid grid-cols-5 gap-4">
            <div>
              <p className="text-xs text-gray-500">Risk Tier</p>
              <StatusBadge status={DEMO_FCA_PRA.pra_ss1_23.model_risk_tier} />
            </div>
            <div>
              <p className="text-xs text-gray-500">Validation</p>
              <StatusBadge status={DEMO_FCA_PRA.pra_ss1_23.model_validation_status} />
            </div>
            <div>
              <p className="text-xs text-gray-500">Inventory</p>
              <BoolBadge value={DEMO_FCA_PRA.pra_ss1_23.model_inventory_complete} trueLabel="COMPLETE" falseLabel="INCOMPLETE" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Monitoring</p>
              <BoolBadge value={DEMO_FCA_PRA.pra_ss1_23.ongoing_monitoring_active} trueLabel="ACTIVE" falseLabel="INACTIVE" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Documentation</p>
              <BoolBadge value={DEMO_FCA_PRA.pra_ss1_23.model_documentation_complete} trueLabel="COMPLETE" falseLabel="INCOMPLETE" />
            </div>
          </div>
        </div>

        {/* SM&CR + DORA */}
        <div className="grid grid-cols-2 gap-6">
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase mb-2">SM&CR Accountability</p>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-gray-500">Mapped</p>
                <BoolBadge value={DEMO_FCA_PRA.smcr.accountability_mapped} />
              </div>
              <div>
                <p className="text-xs text-gray-500">Senior Managers</p>
                <p className="text-sm font-bold text-gray-700">{DEMO_FCA_PRA.smcr.senior_managers_assigned}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">AI Systems</p>
                <p className="text-sm font-bold text-gray-700">{DEMO_FCA_PRA.smcr.ai_systems_covered}</p>
              </div>
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase mb-2">DORA ICT Risk</p>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-gray-500">Status</p>
                <StatusBadge status={DEMO_FCA_PRA.dora.ict_risk_status} />
              </div>
              <div>
                <p className="text-xs text-gray-500">Incident Reporting</p>
                <BoolBadge value={DEMO_FCA_PRA.dora.incident_reporting_ready} trueLabel="READY" falseLabel="NOT READY" />
              </div>
              <div>
                <p className="text-xs text-gray-500">3rd Party Risk</p>
                <BoolBadge value={DEMO_FCA_PRA.dora.third_party_risk_assessed} trueLabel="ASSESSED" falseLabel="NOT ASSESSED" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Seven Sutras Radar (India) */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <h3 className="text-sm font-semibold text-gray-600">India AI Seven Sutras</h3>
          <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded">India</span>
        </div>
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
