import { useEffect, useState } from "react";
import { Review } from "../api/client";
import { Button, Pill } from "../components/ui";

export default function ReviewQueue() {
  const [queue, setQueue] = useState([]);
  const [active, setActive] = useState(null);
  const [context, setContext] = useState(null);
  const [editText, setEditText] = useState("");
  const [busy, setBusy] = useState(false);

  const load = async () => {
    const q = await Review.queue(30);
    setQueue(q);
    return q;
  };

  useEffect(() => {
    load();
  }, []);

  const openCase = async (c) => {
    setActive(c);
    setEditText(c.expected_behavior || "");
    setContext(await Review.context(c.id));
  };

  const act = async (action, extra = {}) => {
    if (!active) return;
    setBusy(true);
    await Review.act(active.id, { action, reviewer: "vaishnavi", ...extra });
    setBusy(false);
    setActive(null);
    setContext(null);
    await load();
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6">
      <div>
        <h1 className="text-xl font-semibold mb-1">Review Queue</h1>
        <p className="text-xs text-ink/50 mb-3">Low-confidence auto-labels, sorted worst first.</p>
        <div className="border border-line rounded-lg bg-white divide-y divide-line max-h-[40vh] lg:max-h-[70vh] overflow-y-auto">
          {queue.map((c) => (
            <button
              key={c.id}
              onClick={() => openCase(c)}
              className={`block w-full text-left p-3 hover:bg-ink/5 ${active?.id === c.id ? "bg-ink/5" : ""}`}
            >
              <div className="text-sm truncate">{c.input}</div>
              <div className="flex gap-2 mt-1">
                <Pill tone={c.confidence < 0.5 ? "warn" : "default"}>
                  confidence {c.confidence.toFixed(2)}
                </Pill>
                <Pill>{c.label_type}</Pill>
              </div>
            </button>
          ))}
          {queue.length === 0 && (
            <div className="p-4 text-sm text-ink/50">Queue is empty. Generate more labels from the Logs page.</div>
          )}
        </div>
      </div>

      <div>
        {!active && (
          <div className="text-sm text-ink/50 border border-dashed border-line rounded-lg p-10 text-center">
            Select a case from the queue to review it.
          </div>
        )}
        {active && (
          <div className="border border-line rounded-lg bg-white p-5">
            <div className="text-xs mono uppercase tracking-wide text-ink/50 mb-1">Input</div>
            <div className="text-sm mb-4">{active.input}</div>

            {context?.original_log && (
              <>
                <div className="text-xs mono uppercase tracking-wide text-ink/50 mb-1">Original response</div>
                <div className="text-sm mb-4 text-ink/70">{context.original_log.response}</div>
              </>
            )}

            <div className="text-xs mono uppercase tracking-wide text-ink/50 mb-1">Expected behavior</div>
            <textarea
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              rows={4}
              className="w-full border border-line rounded p-2 text-sm mb-4"
            />

            <div className="flex gap-2 mb-4 flex-wrap">
              {active.tags.map((t) => <Pill key={t}>{t}</Pill>)}
              <Pill>{active.difficulty}</Pill>
            </div>

            {context?.similar_approved_cases?.length > 0 && (
              <div className="mb-4">
                <div className="text-xs mono uppercase tracking-wide text-ink/50 mb-1">
                  Similar approved cases
                </div>
                <div className="space-y-1">
                  {context.similar_approved_cases.map((s) => (
                    <div key={s.id} className="text-xs text-ink/60 truncate">• {s.input}</div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex flex-wrap gap-2">
              <Button variant="accent" disabled={busy} onClick={() => act("approve")}>Approve</Button>
              <Button
                variant="outline"
                disabled={busy}
                onClick={() => act("edit", { edits: { expected_behavior: editText } })}
              >
                Save edit + approve
              </Button>
              <Button
                variant="warn"
                disabled={busy}
                onClick={() => act("reject", { reason: prompt("Rejection reason?") || "unspecified" })}
              >
                Reject
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
