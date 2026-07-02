export function StatCard({ label, value, accent }) {
  return (
    <div className="border border-line rounded-lg p-4 bg-white">
      <div className="text-xs mono uppercase tracking-wide text-ink/50">{label}</div>
      <div className={`text-2xl font-semibold mt-1 ${accent ? "text-accent" : ""}`}>{value}</div>
    </div>
  );
}

export function Pill({ children, tone = "default" }) {
  const tones = {
    default: "bg-ink/5 text-ink/70",
    good: "bg-accent/10 text-accent",
    warn: "bg-warn/10 text-warn",
  };
  return (
    <span className={`inline-block text-xs mono px-2 py-0.5 rounded ${tones[tone]}`}>
      {children}
    </span>
  );
}

export function Button({ children, onClick, variant = "primary", disabled, className = "" }) {
  const variants = {
    primary: "bg-ink text-paper hover:bg-ink/85",
    outline: "border border-line text-ink hover:bg-ink/5",
    accent: "bg-accent text-white hover:bg-accent/85",
    warn: "bg-warn text-white hover:bg-warn/85",
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`text-sm px-3 py-1.5 rounded transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
}
