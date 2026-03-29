import type { TrustLevel } from "@/types";

const styles: Record<TrustLevel, string> = {
  trusted: "bg-green-100 text-green-800 border-green-300",
  standard: "bg-blue-100 text-blue-800 border-blue-300",
  restricted: "bg-yellow-100 text-yellow-800 border-yellow-300",
  quarantined: "bg-red-100 text-red-800 border-red-300",
};

export function TrustLevelBadge({ level }: { level: TrustLevel }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-medium ${styles[level]}`}>
      {level.toUpperCase()}
    </span>
  );
}
