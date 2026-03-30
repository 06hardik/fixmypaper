"use client";

import { useState, useEffect } from "react";
import DashboardShell from "@/components/DashboardShell";
import {
  ALL_SECTIONS,
  getChecksByCategory,
  fetchFormats,
  createFormat,
  deleteFormat,
} from "@/lib/data";

const checksByCategory = getChecksByCategory();

const DEFAULT_SECTIONS = ["Abstract", "Introduction", "Conclusion", "References"];

export default function ProfessorPage() {
  const [tab, setTab] = useState("create");
  const [formats, setFormats] = useState([]);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState(null);

  // Form state
  const [name, setName] = useState("");
  const [author, setAuthor] = useState("");
  const [desc, setDesc] = useState("");
  const [sections, setSections] = useState(new Set(DEFAULT_SECTIONS));
  const [checks, setChecks] = useState(() => {
    const s = new Set();
    for (const [id, info] of Object.entries(getChecksByCategory()).flatMap(([, arr]) =>
      arr.map((c) => [c.id, c]),
    )) {
      if (info.default) s.add(id);
    }
    return s;
  });

  const loadFormats = () => fetchFormats().then(setFormats);

  useEffect(() => { loadFormats(); }, []);

  const toggleSet = (set, setFn, val) => {
    const next = new Set(set);
    next.has(val) ? next.delete(val) : next.add(val);
    setFn(next);
  };

  const flashMsg = (text, type) => {
    setMsg({ text, type });
    setTimeout(() => setMsg(null), 4000);
  };

  const handleSave = async () => {
    if (!name.trim() || !author.trim()) {
      flashMsg("Please fill in Format Name and Your Name.", "error");
      return;
    }
    if (checks.size === 0) {
      flashMsg("Enable at least one check.", "error");
      return;
    }
    setSaving(true);
    try {
      await createFormat({
        name: name.trim(),
        created_by: author.trim(),
        description: desc.trim(),
        mandatory_sections: [...sections],
        enabled_checks: [...checks],
      });
      flashMsg(`Format "${name}" saved!`, "success");
      setName("");
      setAuthor("");
      setDesc("");
      setSections(new Set(DEFAULT_SECTIONS));
      await loadFormats();
    } catch (err) {
      flashMsg("Error: " + err.message, "error");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id, fmtName) => {
    if (!confirm(`Delete format "${fmtName}"?`)) return;
    try {
      await deleteFormat(id);
      await loadFormats();
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  return (
    <DashboardShell caption="Professor Dashboard">
      <section className="bg-white border border-line rounded-card p-5">
        <h2 className="text-base font-bold mb-1">Format Management</h2>
        <p className="text-xs text-ink-soft mb-4">
          Define publication expectations and deploy them to students instantly.
        </p>

        {/* Tabs */}
        <div className="grid grid-cols-2 border border-line rounded-xl overflow-hidden mb-5">
          {[
            { id: "create", label: "Create Format" },
            { id: "manage", label: "Manage Formats" },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`py-3 text-sm font-semibold transition-colors ${
                tab === t.id
                  ? "bg-blue-50 text-brand-dark"
                  : "bg-panel-muted text-gray-500 hover:text-brand"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Create Tab */}
        {tab === "create" && (
          <div className="animate-fade-in space-y-4">
            {/* Details */}
            <fieldset className="border border-line bg-panel-muted rounded-xl p-4 space-y-3">
              <legend className="text-sm font-bold px-1">Format Details</legend>
              <div className="grid sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold mb-1">Format Name *</label>
                  <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Department Conference Template"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-brand/30 focus:border-brand outline-none transition"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold mb-1">Your Name *</label>
                  <input
                    value={author}
                    onChange={(e) => setAuthor(e.target.value)}
                    placeholder="e.g. Prof. A. Sharma"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-brand/30 focus:border-brand outline-none transition"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold mb-1">Description</label>
                <textarea
                  value={desc}
                  onChange={(e) => setDesc(e.target.value)}
                  rows={2}
                  placeholder="Brief note on where this format should be used."
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm resize-y min-h-[60px] focus:ring-2 focus:ring-brand/30 focus:border-brand outline-none transition"
                />
              </div>
            </fieldset>

            {/* Sections */}
            <fieldset className="border border-line bg-panel-muted rounded-xl p-4">
              <legend className="text-sm font-bold px-1">Mandatory Sections</legend>
              <p className="text-[11px] text-ink-soft mb-3">
                Selected sections become required in student submissions.
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {ALL_SECTIONS.map((sec) => (
                  <label
                    key={sec}
                    className="flex items-center gap-2 text-xs cursor-pointer py-1"
                  >
                    <input
                      type="checkbox"
                      checked={sections.has(sec)}
                      onChange={() => toggleSet(sections, setSections, sec)}
                      className="accent-brand w-4 h-4"
                    />
                    <span>{sec}</span>
                  </label>
                ))}
              </div>
            </fieldset>

            {/* Checks */}
            <fieldset className="border border-line bg-panel-muted rounded-xl p-4">
              <legend className="text-sm font-bold px-1">Enabled Checks</legend>
              <p className="text-[11px] text-ink-soft mb-3">
                Only enabled checks appear in student quality reports.
              </p>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {Object.entries(checksByCategory).map(([cat, items]) => (
                  <div key={cat} className="border border-gray-200 rounded-lg bg-white p-3">
                    <h4 className="text-xs font-bold mb-2">{cat}</h4>
                    {items.map((chk) => (
                      <label
                        key={chk.id}
                        className="flex items-center gap-2 text-xs cursor-pointer py-1"
                        title={chk.description}
                      >
                        <input
                          type="checkbox"
                          checked={checks.has(chk.id)}
                          onChange={() => toggleSet(checks, setChecks, chk.id)}
                          className="accent-brand w-4 h-4"
                        />
                        <span>{chk.name}</span>
                      </label>
                    ))}
                  </div>
                ))}
              </div>
            </fieldset>

            {/* Save */}
            <button
              onClick={handleSave}
              disabled={saving}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-brand to-brand-dark text-white text-sm font-semibold hover:shadow-lift transition-all disabled:opacity-50"
            >
              {saving ? "Saving…" : "Save Format"}
            </button>
            {msg && (
              <div
                className={`text-center text-sm font-semibold rounded-lg px-4 py-2.5 ${
                  msg.type === "success"
                    ? "bg-green-50 text-green-700"
                    : "bg-red-50 text-red-700"
                }`}
              >
                {msg.text}
              </div>
            )}
          </div>
        )}

        {/* Manage Tab */}
        {tab === "manage" && (
          <div className="animate-fade-in space-y-3">
            {formats.length === 0 && (
              <p className="text-center text-sm text-ink-soft py-8">
                No formats saved yet. Create one above.
              </p>
            )}
            {formats.map((fmt) => (
              <div
                key={fmt.id}
                className={`border rounded-xl p-4 bg-panel-muted ${
                  fmt.is_system ? "border-l-4 border-l-brand border-line" : "border-line"
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <h4 className="text-sm font-bold">
                    {fmt.name}
                    {fmt.is_system && (
                      <span className="ml-2 text-[10px] font-bold uppercase bg-blue-50 text-brand-dark px-2 py-0.5 rounded-full">
                        System
                      </span>
                    )}
                  </h4>
                  <span className="text-xs text-ink-soft">by {fmt.created_by}</span>
                </div>
                {fmt.description && (
                  <p className="text-xs text-ink-soft mb-2">{fmt.description}</p>
                )}
                <div className="flex flex-wrap gap-1 mb-2">
                  {(fmt.mandatory_sections || []).map((s) => (
                    <span
                      key={s}
                      className="text-[10px] bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full"
                    >
                      {s}
                    </span>
                  ))}
                  {(!fmt.mandatory_sections || fmt.mandatory_sections.length === 0) && (
                    <span className="text-[10px] text-ink-soft italic">No sections</span>
                  )}
                </div>
                <p className="text-xs text-ink-soft mb-2">
                  {fmt.enabled_checks?.length || 0} checks enabled
                </p>
                {!fmt.is_system && (
                  <button
                    onClick={() => handleDelete(fmt.id, fmt.name)}
                    className="px-3 py-1.5 rounded-lg bg-red-50 text-red-700 text-xs font-semibold hover:bg-red-100 transition"
                  >
                    Delete
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </section>
    </DashboardShell>
  );
}
