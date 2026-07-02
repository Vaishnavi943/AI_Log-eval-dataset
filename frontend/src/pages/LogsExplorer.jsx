import { useEffect, useState } from "react";
import { Logs, Sampling, Labeling } from "../api/client";
import { Button, Pill } from "../components/ui";
import AddLogForm from "../components/AddLogForm.jsx";

export default function LogsExplorer() {
  const [logs, setLogs] = useState([]);
  const [selected, setSelected] = useState(new Set());
  const [mode, setMode] = useState("random");
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [filters, setFilters] = useState({ feature_name: "", error_status: "", user_feedback: "" });

  const load = async () => {
    setLoading(true);
    const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
    setLogs(await Logs.list({ ...params, limit: 50 }));
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, []);

  const runSample = async () => {
    setLoading(true);
    setLogs(await Sampling.run(mode, 50));
    setLoading(false);
  };

  const toggle = (id) => {
    const next = new Set(selected);
    next.has(id) ? next.delete(id) : next.add(id);
    setSelected(next);
  };

  const generateForSelected = async () => {
    if (selected.size === 0) return;
    setGenerating(true);
    await Labeling.generate(Array.from(selected));
    setGenerating(false);
    setSelected(new Set());
    alert(`Generated eval-case drafts for ${selected.size} logs. Check the Review Queue.`);
  };

  const loadCandidates = async () => {
    setLoading(true);
    const c = await Labeling.candidates(50);
    setLogs(c.map((x) => ({ ...x, prompt: x.prompt, created_at: null })));
    setLoading(false);
  };

  return (
    <div>
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 mb-4">
        <h1 className="text-xl font-semibold">Logs</h1>
        <div className="flex flex-wrap gap-2 items-center">
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            className="text-sm border border-line rounded px-2 py-1.5"
          >
            <option value="random">Random sample</option>
            <option value="failure_biased">Failure-biased sample</option>
            <option value="diversity">Diversity sample</option>
          </select>
          <Button variant="outline" onClick={runSample}>Run sampling</Button>
          <Button variant="outline" onClick={loadCandidates}>High-value candidates</Button>
          <Button variant="outline" onClick={load}>Reset filters</Button>
        </div>
      </div>

      <AddLogForm onCreated={load} />

      <div className="flex flex-wrap gap-2 mb-4">
        <input
          placeholder="feature_name"
          value={filters.feature_name}
          onChange={(e) => setFilters({ ...filters, feature_name: e.target.value })}
          className="text-sm border border-line rounded px-2 py-1.5 w-full sm:w-40"
        />
        <input
          placeholder="error_status"
          value={filters.error_status}
          onChange={(e) => setFilters({ ...filters, error_status: e.target.value })}
          className="text-sm border border-line rounded px-2 py-1.5 w-full sm:w-40"
        />
        <select
          value={filters.user_feedback}
          onChange={(e) => setFilters({ ...filters, user_feedback: e.target.value })}
          className="text-sm border border-line rounded px-2 py-1.5"
        >
          <option value="">any feedback</option>
          <option value="positive">positive</option>
          <option value="negative">negative</option>
        </select>
        <Button variant="outline" onClick={load}>Apply</Button>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
        <div className="text-sm text-ink/60">{logs.length} logs · {selected.size} selected</div>
        <Button variant="accent" onClick={generateForSelected} disabled={generating || selected.size === 0} className="w-full sm:w-auto">
          {generating ? "Generating labels…" : `Generate eval labels (${selected.size})`}
        </Button>
      </div>

      <div className="border border-line rounded-lg bg-white divide-y divide-line">
        {loading && <div className="p-4 text-sm text-ink/50">Loading…</div>}
        {!loading && logs.map((log) => (
          <div key={log.id} className="p-3 flex gap-3 items-start hover:bg-ink/5">
            <input
              type="checkbox"
              checked={selected.has(log.id)}
              onChange={() => toggle(log.id)}
              className="mt-1"
            />
            <div className="flex-1 min-w-0">
              <div className="text-sm truncate">{log.prompt}</div>
              <div className="flex gap-2 mt-1 flex-wrap">
                {log.feature_name && <Pill>{log.feature_name}</Pill>}
                {log.error_status && <Pill tone="warn">{log.error_status}</Pill>}
                {log.user_feedback === "negative" && <Pill tone="warn">negative feedback</Pill>}
                {log.user_feedback === "positive" && <Pill tone="good">positive feedback</Pill>}
                {log.is_redacted && <Pill>redacted</Pill>}
              </div>
            </div>
          </div>
        ))}
        {!loading && logs.length === 0 && (
          <div className="p-6 text-sm text-ink/50 text-center">No logs yet — seed some from the Dashboard.</div>
        )}
      </div>
    </div>
  );
}
