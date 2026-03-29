export function ThreatScoreBadge({ score }: { score: number }) {
  const color =
    score >= 0.8 ? "bg-red-500" : score >= 0.6 ? "bg-orange-500" : score >= 0.3 ? "bg-yellow-500" : "bg-green-500";
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold text-white ${color}`}>
      {(score * 100).toFixed(0)}%
    </span>
  );
}
