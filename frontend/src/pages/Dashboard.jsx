import { useEffect, useState } from "react";
import { Logs, Exports } from "../api/client";
import { StatCard, Button } from "../components/ui";

export default function Dashboard() {
  const [logStats, setLogStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [seeding, setSeeding] = useState(false);

  const load = async () => {
    setLogStats(await Logs.stats());
    setHealth(await Exports.health());
  };

  useEffect(() => {
    load();
  }, []);

  const seed = async () => {
    setSeeding(true);
    await Logs.seed(1000);
    await load();
    setSeeding(false);
  };

  return (
    <div className="max-w-5xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <div>
          <h1 className="text-xl font-semibold">Dataset Flywheel</h1>
          <p className="text-sm text-ink/60 mt-1">
            Logs enter → candidates get selected → labels get generated → humans approve → the eval dataset grows.
          </p>
        </div>
        <Button onClick={seed} disabled={seeding} variant="accent" className="w-full sm:w-auto shrink-0">
          {seeding ? "Seeding…" : "Seed 1,000 synthetic logs"}
        </Button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        <StatCard label="Total Logs" value={logStats?.total_logs ?? "–"} />
        <StatCard label="Redacted" value={logStats?.redacted_logs ?? "–"} />
        <StatCard label="Error Logs" value={logStats?.error_logs ?? "–"} />
        <StatCard label="Negative Feedback" value={logStats?.negative_feedback_logs ?? "–"} />
      </div>

      <h2 className="text-sm mono uppercase tracking-wide text-ink/50 mb-3">Eval Dataset Health</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        <StatCard label="Total Eval Cases" value={health?.total_cases ?? "–"} accent />
        <StatCard label="Auto-labeled %" value={health ? `${health.auto_labeled_pct}%` : "–"} />
        <StatCard label="Human-reviewed %" value={health ? `${health.human_reviewed_pct}%` : "–"} />
        <StatCard label="Approved" value={health?.by_status?.approved ?? "–"} accent />
      </div>

      {health && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <BreakdownTable title="By status" data={health.by_status} />
          <BreakdownTable title="By difficulty" data={health.by_difficulty} />
        </div>
      )}

      <div className="mt-8 border border-line rounded-lg p-4 bg-white text-sm text-ink/70">
        <span className="mono text-accent">Pipeline order:</span> Dashboard (seed) → Logs (inspect) →
        Clusters (embed + group) → Review Queue (approve/edit/reject) → Export (JSONL + health).
      </div>
    </div>
  );
}

function BreakdownTable({ title, data }) {
  return (
    <div className="border border-line rounded-lg bg-white p-4">
      <div className="text-xs mono uppercase tracking-wide text-ink/50 mb-2">{title}</div>
      <div className="space-y-1">
        {Object.entries(data).map(([k, v]) => (
          <div key={k} className="flex justify-between text-sm">
            <span className="text-ink/70">{k}</span>
            <span className="mono">{v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
