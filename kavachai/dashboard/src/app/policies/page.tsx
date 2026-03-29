"use client";

import { useState } from "react";

interface PolicyRow {
  policy_id: string;
  name: string;
  status: "active" | "inactive";
  rule_count: number;
  dsl_preview: string;
}

const DEMO_POLICIES: PolicyRow[] = [
  {
    policy_id: "pol-001",
    name: "financial_services_safety",
    status: "active",
    rule_count: 4,
    dsl_preview: `policy financial_services_safety
version "1.0"

rule block_unauthorized_payment {
  when tool_call("payment_process")
  check action.params.amount > 50000
    and agent.trust_level != "trusted"
  then escalate severity critical
}

rule prevent_aadhaar_exfiltration {
  when tool_call("send_email" | "external_api")
  check data_from "customer_records" reaches "external"
  then quarantine severity critical
}`,
  },
  {
    policy_id: "pol-002",
    name: "customer_service_workflow",
    status: "active",
    rule_count: 0,
    dsl_preview: `policy customer_service_workflow
version "1.0"

workflow customer_service {
  state start initial
  state authenticated
  state data_accessed
  state response_sent accepting
  state admin_access dangerous

  start -> authenticated on tool_call("verify_identity")
  authenticated -> data_accessed on tool_call("customer_lookup")
}`,
  },
];

export default function PolicyPage() {
  const [selected, setSelected] = useState<PolicyRow | null>(DEMO_POLICIES[0]);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Policy Management</h2>

      <div className="grid grid-cols-3 gap-6">
        {/* Policy List */}
        <div className="col-span-1 bg-white rounded-lg border shadow-sm p-4">
          <h3 className="text-sm font-semibold text-gray-600 mb-3">Loaded Policies</h3>
          <div className="space-y-2">
            {DEMO_POLICIES.map((pol) => (
              <button
                key={pol.policy_id}
                onClick={() => setSelected(pol)}
                className={`w-full text-left p-3 rounded text-sm transition-colors ${selected?.policy_id === pol.policy_id ? "bg-kavach-50 border border-kavach-500" : "hover:bg-gray-50 border border-transparent"}`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{pol.name}</span>
                  <span className={`text-xs font-bold ${pol.status === "active" ? "text-green-600" : "text-gray-400"}`}>
                    {pol.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{pol.rule_count} rules</p>
              </button>
            ))}
          </div>
        </div>

        {/* DSL Editor / Preview */}
        <div className="col-span-2 bg-white rounded-lg border shadow-sm p-4">
          <h3 className="text-sm font-semibold text-gray-600 mb-3">
            {selected ? selected.name : "Select a policy"}
          </h3>
          {selected && (
            <pre className="bg-gray-900 text-green-400 rounded-lg p-4 text-xs font-mono overflow-auto max-h-[500px] whitespace-pre-wrap">
              {selected.dsl_preview}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
