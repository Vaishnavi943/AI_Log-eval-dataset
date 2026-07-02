import { useEffect, useState } from "react";
import { Exports } from "../api/client";
import { StatCard, Button } from "../components/ui";

export default function ExportHealth() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    Exports.health().then(setHealth);
  }, []);

  return (
    <div className="max-w-3xl">
      <h1 className="text-xl font-semibold mb-1">Export</h1>
      <p className="text-sm text-ink/60 mb-6">
        Only <span className="mono">approved</span> cases are included in the exported dataset.
      </p>

      {health && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <StatCard label="Approved cases" value={health.by_status.approved} accent />
          <StatCard label="Draft" value={health.by_status.draft} />
          <StatCard label="Rejected" value={health.by_status.rejected} />
          <StatCard label="Human-reviewed %" value={`${health.human_reviewed_pct}%`} />
        </div>
      )}

      <a href={Exports.jsonlUrl()}>
        <Button variant="accent">Download eval_dataset.jsonl</Button>
      </a>

      <div className="mt-8 border border-line rounded-lg bg-white p-4 text-sm">
        <div className="mono text-xs uppercase tracking-wide text-ink/50 mb-2">Portfolio numbers</div>
        <p className="text-ink/70">
          e.g. "Generated {health?.total_cases ?? "N"} approved eval cases across{" "}
          {health ? Object.keys(health.by_label_type).length : "N"} label types, with{" "}
          {health?.auto_labeled_pct ?? "N"}% auto-label acceptance after review."
        </p>
      </div>
    </div>
  );
}
