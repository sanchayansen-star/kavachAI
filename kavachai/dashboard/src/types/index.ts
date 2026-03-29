// Types matching backend Pydantic models

export type VerdictType = "allow" | "block" | "flag" | "escalate" | "quarantine";
export type TrustLevel = "trusted" | "standard" | "restricted" | "quarantined";
export type SeverityLevel = "low" | "medium" | "high" | "critical";

export interface ActionRequest {
  request_id: string;
  agent_id: string;
  session_id: string;
  tool_name: string;
  parameters: Record<string, unknown>;
  timestamp: string;
  tenant_id: string;
}

export interface ActionVerdict {
  verdict: VerdictType;
  reason: string;
  matched_policies: string[];
  threat_score: number;
  ethics_score: number;
  grounding_score: number | null;
}

export interface AuditEntry {
  entry_id: number;
  timestamp: string;
  session_id: string;
  agent_identity_hash: string;
  action_type: string;
  action_verdict: VerdictType;
  threat_score: number;
  ethics_score: number | null;
  entry_hash: string;
  sequence_number: number;
}

export interface KillChainStage {
  stage_number: number;
  category: string;
  description: string;
  threat_score: number;
  timestamp: string;
}

export interface KillChain {
  kill_chain_id: string;
  session_id: string;
  stages: KillChainStage[];
  overall_threat_score: number;
  is_stac_attack: boolean;
}

export interface Escalation {
  escalation_id: string;
  action_request: ActionRequest;
  threat_score: number;
  kill_chain_id: string | null;
  timeout_at: string;
  status: string;
}

export interface DashboardEvent {
  type: "threat_update" | "escalation" | "kill_chain" | "quarantine" | "trust_change" | "grounding_alert";
  [key: string]: unknown;
}

export interface SevenSutrasScores {
  trust: number;
  people_first: number;
  innovation: number;
  fairness: number;
  accountability: number;
  understandable: number;
  safety: number;
}
