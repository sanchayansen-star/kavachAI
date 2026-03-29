export function HashChainIndicator({ valid }: { valid: boolean }) {
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium ${valid ? "text-green-600" : "text-red-600"}`}>
      <span className={`w-2 h-2 rounded-full ${valid ? "bg-green-500" : "bg-red-500"}`} />
      {valid ? "Chain Valid" : "Chain Broken"}
    </span>
  );
}
