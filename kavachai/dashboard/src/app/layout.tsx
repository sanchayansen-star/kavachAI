import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KavachAI — SOC Dashboard",
  description: "Zero Trust Safety Firewall for Agentic AI",
};

const navItems = [
  { href: "/", label: "Threat Feed", icon: "🛡️" },
  { href: "/kill-chains", label: "Kill Chains", icon: "⛓️" },
  { href: "/escalations", label: "Escalations", icon: "🔶" },
  { href: "/forensics", label: "Forensics", icon: "🔍" },
  { href: "/compliance", label: "Compliance", icon: "📋" },
  { href: "/agents", label: "Agents", icon: "🤖" },
  { href: "/policies", label: "Policies", icon: "📜" },
  { href: "/model-eval", label: "Model Eval", icon: "🧪" },
  { href: "/llm-usage", label: "LLM Usage", icon: "💰" },
  { href: "/grounding", label: "Grounding", icon: "📌" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex h-screen overflow-hidden">
        <aside className="w-56 bg-kavach-900 text-white flex flex-col shrink-0">
          <div className="p-4 border-b border-kavach-700">
            <h1 className="text-lg font-bold tracking-tight">🛡️ KavachAI</h1>
            <p className="text-xs text-kavach-50/60 mt-0.5">SOC Dashboard</p>
          </div>
          <nav className="flex-1 py-2 overflow-y-auto" aria-label="Main navigation">
            {navItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-kavach-700 transition-colors"
              >
                <span>{item.icon}</span>
                {item.label}
              </a>
            ))}
          </nav>
        </aside>
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </body>
    </html>
  );
}
