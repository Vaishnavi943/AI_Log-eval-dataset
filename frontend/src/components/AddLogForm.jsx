import { useState } from "react";
import { Logs } from "../api/client";
import { Button } from "./ui";

const EMPTY = {
  prompt: "",
  response: "",
  system_prompt: "",
  model: "manual-entry",
  feature_name: "manual",
  user_feedback: "",
  error_status: "",
};

export default function AddLogForm({ onCreated }) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    if (!form.prompt.trim() || !form.response.trim()) return;
    setSaving(true);
    const payload = {
      ...form,
      user_feedback: form.user_feedback || null,
      error_status: form.error_status || null,
      system_prompt: form.system_prompt || null,
    };
    await Logs.create(payload);
    setSaving(false);
    setForm(EMPTY);
    setOpen(false);
    onCreated?.();
  };

  if (!open) {
    return (
      <Button variant="outline" onClick={() => setOpen(true)}>
        + Add log manually
      </Button>
    );
  }

  return (
    <form onSubmit={submit} className="border border-line rounded-lg bg-white p-4 mb-4 space-y-3">
      <div className="flex justify-between items-center">
        <div className="text-sm font-medium">Add a log</div>
        <button type="button" onClick={() => setOpen(false)} className="text-xs text-ink/50 hover:text-ink">
          cancel
        </button>
      </div>

      <div>
        <label className="text-xs mono uppercase tracking-wide text-ink/50">Prompt *</label>
        <textarea
          required
          value={form.prompt}
          onChange={update("prompt")}
          rows={2}
          className="w-full border border-line rounded p-2 text-sm mt-1"
          placeholder="What the user asked"
        />
      </div>

      <div>
        <label className="text-xs mono uppercase tracking-wide text-ink/50">Response *</label>
        <textarea
          required
          value={form.response}
          onChange={update("response")}
          rows={2}
          className="w-full border border-line rounded p-2 text-sm mt-1"
          placeholder="What the model answered"
        />
      </div>

      <div>
        <label className="text-xs mono uppercase tracking-wide text-ink/50">System prompt</label>
        <input
          value={form.system_prompt}
          onChange={update("system_prompt")}
          className="w-full border border-line rounded p-2 text-sm mt-1"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs mono uppercase tracking-wide text-ink/50">Feature name</label>
          <input
            value={form.feature_name}
            onChange={update("feature_name")}
            className="w-full border border-line rounded p-2 text-sm mt-1"
          />
        </div>
        <div>
          <label className="text-xs mono uppercase tracking-wide text-ink/50">Model</label>
          <input
            value={form.model}
            onChange={update("model")}
            className="w-full border border-line rounded p-2 text-sm mt-1"
          />
        </div>
        <div>
          <label className="text-xs mono uppercase tracking-wide text-ink/50">User feedback</label>
          <select
            value={form.user_feedback}
            onChange={update("user_feedback")}
            className="w-full border border-line rounded p-2 text-sm mt-1"
          >
            <option value="">none</option>
            <option value="positive">positive</option>
            <option value="negative">negative</option>
          </select>
        </div>
        <div>
          <label className="text-xs mono uppercase tracking-wide text-ink/50">Error status</label>
          <input
            value={form.error_status}
            onChange={update("error_status")}
            placeholder="e.g. timeout"
            className="w-full border border-line rounded p-2 text-sm mt-1"
          />
        </div>
      </div>

      <Button type="submit" variant="accent" disabled={saving}>
        {saving ? "Saving…" : "Save log"}
      </Button>
    </form>
  );
}
