import type { VerdictType } from "@/types";

const colors: Record<VerdictType, string> = {
  allow: "bg-green-100 text-green-800",
  block: "bg-red-100 text-red-800",
  flag: "bg-yellow-100 text-yellow-800",
  escalate: "bg-orange-100 text-orange-800",
  quarantine: "bg-purple-100 text-purple-800",
};

export function VerdictChip({ verdict }: { verdict: VerdictType }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[verdict]}`}>
      {verdict.toUpperCase()}
    </span>
  );
}
