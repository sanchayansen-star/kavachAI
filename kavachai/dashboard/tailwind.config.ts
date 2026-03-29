import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        kavach: { 50: "#f0f9ff", 500: "#0ea5e9", 700: "#0369a1", 900: "#0c4a6e" },
        threat: { low: "#22c55e", medium: "#eab308", high: "#f97316", critical: "#ef4444" },
      },
    },
  },
  plugins: [],
};
export default config;
