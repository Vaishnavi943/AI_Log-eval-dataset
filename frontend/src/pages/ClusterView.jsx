import { useEffect, useState } from "react";
import { Clusters } from "../api/client";
import { Button, StatCard } from "../components/ui";

export default function ClusterView() {
  const [clusters, setClusters] = useState([]);
  const [running, setRunning] = useState(false);
  const [minSize, setMinSize] = useState(5);
  const [algorithm, setAlgorithm] = useState("hdbscan");

  const load = async () => setClusters(await Clusters.list());

  useEffect(() => {
    load();
  }, []);

  const run = async () => {
    setRunning(true);
    await Clusters.run({ min_cluster_size: Number(minSize), algorithm });
    await load();
    setRunning(false);
  };

  const totalLogs = clusters.reduce((s, c) => s + c.log_count, 0);
  const avgCoverage = clusters.length
    ? Math.round((clusters.reduce((s, c) => s + c.eval_coverage, 0) / clusters.length) * 100)
    : 0;

  return (
    <div>
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 mb-4">
        <h1 className="text-xl font-semibold">Clusters</h1>
        <div className="flex flex-wrap gap-2 items-center">
          <select
            value={algorithm}
            onChange={(e) => setAlgorithm(e.target.value)}
            className="text-sm border border-line rounded px-2 py-1.5"
          >
            <option value="hdbscan">HDBSCAN</option>
            <option value="kmeans">KMeans</option>
          </select>
          <input
            type="number"
            value={minSize}
            onChange={(e) => setMinSize(e.target.value)}
            className="text-sm border border-line rounded px-2 py-1.5 w-20"
            title="min cluster size"
          />
          <Button variant="accent" onClick={run} disabled={running} className="w-full sm:w-auto">
            {running ? "Embedding + clustering…" : "Run clustering"}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
        <StatCard label="Clusters found" value={clusters.length} />
        <StatCard label="Logs clustered" value={totalLogs} />
        <StatCard label="Avg eval coverage" value={`${avgCoverage}%`} accent />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {clusters.map((c) => (
          <div key={c.id} className="border border-line rounded-lg bg-white p-4">
            <div className="text-sm font-medium truncate">{c.label}</div>
            <div className="text-xs text-ink/50 mono mt-1">{c.algorithm}</div>
            <div className="flex justify-between items-center mt-3 text-sm">
              <span>{c.log_count} logs</span>
              <CoverageBar pct={c.eval_coverage * 100} />
            </div>
          </div>
        ))}
        {clusters.length === 0 && (
          <div className="col-span-2 text-sm text-ink/50 text-center border border-dashed border-line rounded-lg p-8">
            No clusters yet. Seed logs on the Dashboard, then run clustering here.
          </div>
        )}
      </div>
    </div>
  );
}

function CoverageBar({ pct }) {
  return (
    <div className="flex items-center gap-2 w-28">
      <div className="flex-1 h-1.5 bg-ink/10 rounded overflow-hidden">
        <div className="h-full bg-accent" style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <span className="text-xs mono">{Math.round(pct)}%</span>
    </div>
  );
}
