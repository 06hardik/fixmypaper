"use client";

import { useState, useEffect, useCallback } from "react";
import DashboardShell from "@/components/DashboardShell";
import { fetchFormats, uploadPDF, downloadURL, ERROR_DESCRIPTIONS } from "@/lib/data";

const FILTER_GROUPS = {
  all: null,
  missing_required_section: ["missing_required_section"],
  metadata_incomplete: ["metadata_incomplete"],
  abstract_word_count: ["abstract_word_count"],
  structure: ["missing_abstract", "missing_index_terms", "missing_references", "non_roman_heading", "missing_introduction"],
  numbering: ["invalid_figure_label", "invalid_table_numbering", "equation_numbering"],
  sequence: ["figure_numbering_sequence", "table_numbering_sequence", "reference_numbering_sequence"],
  caption_placement: ["caption_placement"],
  url_doi: ["broken_url", "broken_doi"],
  writing_style: ["writing_style"],
};

const FILTER_LABELS = {
  all: "All",
  missing_required_section: "Sections",
  metadata_incomplete: "Metadata",
  abstract_word_count: "Abstract",
  structure: "Structure",
  numbering: "Labels",
  sequence: "Sequence",
  caption_placement: "Captions",
  url_doi: "URLs / DOIs",
  writing_style: "Writing",
};

export default function StudentPage() {
  const [formats, setFormats] = useState([]);
  const [formatId, setFormatId] = useState("");
  const [phase, setPhase] = useState("upload"); // upload | processing | results
  const [fileName, setFileName] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    fetchFormats().then((f) => {
      setFormats(f);
      if (f.length) setFormatId(f[0].id);
    });
  }, []);

  const handleFile = useCallback(
    async (file) => {
      setError("");
      if (!file.name.toLowerCase().endsWith(".pdf")) {
        setError("Please upload a PDF file.");
        return;
      }
      if (file.size > 50 * 1024 * 1024) {
        setError("File size must be less than 50 MB.");
        return;
      }

      setFileName(file.name);
      setPhase("processing");

      try {
        const data = await uploadPDF(file, formatId);
        if (data.success) {
          setResult(data);
          setPhase("results");
          setActiveTab("overview");
          setFilter("all");
        } else {
          throw new Error("Processing failed");
        }
      } catch (err) {
        setError(err.message);
        setPhase("upload");
      }
    },
    [formatId],
  );

  const reset = () => {
    setPhase("upload");
    setResult(null);
    setFileName("");
    setFilter("all");
    setActiveTab("overview");
    setError("");
  };

  const onDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
  };

  return (
    <DashboardShell caption="Student Dashboard">
      {/* Format selector */}
      <section className="bg-white border border-line rounded-card p-5">
        <h2 className="text-base font-bold mb-1">Submission Format</h2>
        <p className="text-xs text-ink-soft mb-3">Select the format your paper should match.</p>
        <select
          value={formatId}
          onChange={(e) => setFormatId(e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand transition"
        >
          {formats.length === 0 && <option value="">No formats available</option>}
          {formats.map((f) => (
            <option key={f.id} value={f.id}>
              {f.name} — by {f.created_by}
            </option>
          ))}
        </select>
      </section>

      {/* Upload */}
      {phase === "upload" && (
        <section className="bg-white border border-line rounded-card p-5 animate-fade-in">
          <div
            onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add("border-brand", "bg-blue-50/50"); }}
            onDragLeave={(e) => { e.currentTarget.classList.remove("border-brand", "bg-blue-50/50"); }}
            onDrop={onDrop}
            onClick={() => document.getElementById("file-input").click()}
            className="border-2 border-dashed border-gray-300 rounded-xl py-14 px-6 text-center cursor-pointer transition-all hover:border-brand hover:bg-blue-50/30"
          >
            <svg className="w-10 h-10 mx-auto text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
            </svg>
            <h3 className="font-semibold text-base mb-1">Upload Manuscript</h3>
            <p className="text-sm text-ink-soft mb-4">
              Drop a PDF here, or click to browse. Max 50 MB.
            </p>
            <input
              id="file-input"
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => e.target.files.length && handleFile(e.target.files[0])}
            />
            <button
              type="button"
              className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-brand to-brand-dark text-white text-sm font-semibold hover:shadow-lift transition-all"
              onClick={(e) => { e.stopPropagation(); document.getElementById("file-input").click(); }}
            >
              Choose PDF
            </button>
            {fileName && (
              <p className="mt-3 text-xs font-semibold text-brand-dark">
                Selected: {fileName}
              </p>
            )}
          </div>
          {!fileName && (
            <div className="mt-4 border border-line rounded-xl bg-panel-muted p-4 text-center">
              <p className="text-sm font-semibold text-ink mb-0.5">No file uploaded yet</p>
              <p className="text-xs text-ink-soft">Upload a PDF to generate a full formatting quality report.</p>
            </div>
          )}
          {error && (
            <div className="mt-3 border border-red-200 bg-red-50 text-red-800 rounded-xl px-4 py-3 text-sm font-semibold">
              {error}
            </div>
          )}
        </section>
      )}

      {/* Processing */}
      {phase === "processing" && (
        <section className="bg-white border border-line rounded-card p-10 text-center animate-fade-in">
          <div className="spinner mx-auto mb-5" />
          <h3 className="text-lg font-bold mb-1">Analyzing document quality&hellip;</h3>
          <p className="text-sm text-ink-soft">Please wait while your report is being prepared.</p>
        </section>
      )}

      {/* Results */}
      {phase === "results" && result && (
        <ResultsView
          result={result}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          filter={filter}
          setFilter={setFilter}
          onReset={reset}
        />
      )}
    </DashboardShell>
  );
}

/* ── Results sub-component ────────────────────────────────────────────── */

function ResultsView({ result, activeTab, setActiveTab, filter, setFilter, onReset }) {
  const overview = result.document_overview || {};
  const stats = result.statistics || {};
  const errors = result.errors || [];
  const refAnalysis = result.reference_analysis;

  const uniquePages = new Set(errors.map((e) => e.page_num)).size;

  const filteredErrors = (() => {
    if (filter === "all") return errors;
    const types = FILTER_GROUPS[filter];
    if (!types) return errors;
    return errors.filter((e) => types.includes(e.error_type));
  })();

  const errorsByType = {};
  errors.forEach((e) => {
    if (!errorsByType[e.error_type]) errorsByType[e.error_type] = { count: 0, name: e.check_name, checkId: e.check_id };
    errorsByType[e.error_type].count++;
  });

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "sections", label: "Sections" },
    { id: "insights", label: "Insights" },
  ];

  return (
    <section className="bg-white border border-line rounded-card p-5 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
        <h2 className="text-lg font-bold text-green-700">Quality Report Ready</h2>
        <a
          href={downloadURL(result.job_id)}
          className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-green-700 to-green-800 text-white text-sm font-semibold hover:shadow-lift transition-all"
        >
          Download Annotated PDF
        </a>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-line pb-3 mb-5">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold border transition-all ${
              activeTab === t.id
                ? "bg-blue-50 border-blue-300 text-brand-dark"
                : "bg-white border-gray-200 text-gray-500 hover:border-brand/40 hover:text-brand"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab: Overview */}
      {activeTab === "overview" && (
        <div className="animate-fade-in space-y-4">
          <div className="grid sm:grid-cols-2 gap-3">
            <Card label="Title" value={overview.title || result.original_filename || "-"} />
            <Card label="Authors" value={overview.authors || "Not detected"} />
          </div>
          <Card label="Abstract" value={overview.abstract || "Not detected"} wide />

          {/* KPI row */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
            <KPI value={result.error_count} label="Errors" />
            <KPI value={uniquePages} label="Pages w/ errors" />
            <KPI value={stats.total_figures || 0} label="Figures" />
            <KPI value={stats.total_tables || 0} label="Tables" />
            <KPI value={stats.total_equations || 0} label="Equations" />
          </div>

          {/* Sections status */}
          <SectionsStatus mandatory={result.mandatory_sections} errors={errors} />
        </div>
      )}

      {/* Tab: Sections */}
      {activeTab === "sections" && (
        <div className="animate-fade-in space-y-4">
          {/* Summary cards */}
          {Object.keys(errorsByType).length > 0 && (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {Object.entries(errorsByType).map(([type, info]) => (
                <div key={type} className="flex items-center justify-between border border-line rounded-xl bg-panel-muted p-3">
                  <div>
                    <p className="text-xs font-semibold">{info.name}</p>
                    <p className="text-[11px] text-ink-soft">{ERROR_DESCRIPTIONS[type] || type}</p>
                  </div>
                  <span className="text-lg font-extrabold text-brand-dark">{info.count}</span>
                </div>
              ))}
            </div>
          )}

          {/* Filters */}
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(FILTER_LABELS).map(([key, label]) => (
              <button
                key={key}
                onClick={() => setFilter(key)}
                className={`px-3 py-1.5 rounded-full text-[11px] font-semibold border transition-all ${
                  filter === key
                    ? "bg-brand text-white border-brand"
                    : "bg-white border-gray-200 text-gray-500 hover:border-brand/40"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Error list */}
          <div className="space-y-2.5">
            {filteredErrors.length === 0 && (
              <p className="text-center text-sm text-ink-soft py-6">
                No errors found for this filter.
              </p>
            )}
            {filteredErrors.map((err, i) => (
              <div
                key={i}
                className="border border-red-100 bg-red-50/40 border-l-4 border-l-red-600 rounded-xl p-3.5"
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <p className="text-sm font-semibold">
                    Check #{err.check_id}: {err.check_name}
                  </p>
                  <span className="shrink-0 bg-blue-50 text-brand-dark text-[11px] font-semibold px-2.5 py-0.5 rounded-full">
                    Page {err.page_num}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-1.5 leading-relaxed">{err.description}</p>
                <p className="text-xs font-mono bg-white border border-gray-200 rounded-lg px-2.5 py-1.5 break-all">
                  Found: &ldquo;{err.text}&rdquo;
                </p>
              </div>
            ))}
          </div>

          <div className="text-center pt-2">
            <button onClick={onReset} className="px-5 py-2.5 rounded-lg bg-gray-100 text-sm font-semibold text-ink hover:bg-gray-200 transition">
              Upload Another PDF
            </button>
          </div>
        </div>
      )}

      {/* Tab: Insights */}
      {activeTab === "insights" && (
        <div className="animate-fade-in space-y-4">
          {/* Key insights */}
          <Card label="Key Insights" wide>
            <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
              {(overview.key_insights || []).map((item, i) => (
                <li key={i}>{item}</li>
              ))}
              {(!overview.key_insights || overview.key_insights.length === 0) && (
                <li>No additional insights available.</li>
              )}
            </ul>
          </Card>

          {/* Reference analysis */}
          {refAnalysis && !refAnalysis.error && (
            <ReferenceAnalysis data={refAnalysis} />
          )}
        </div>
      )}
    </section>
  );
}

/* ── Small UI pieces ──────────────────────────────────────────────────── */

function Card({ label, value, wide, children }) {
  return (
    <div className={`border border-line bg-panel-muted rounded-xl p-4 ${wide ? "" : ""}`}>
      <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">{label}</p>
      {children || <p className="text-sm text-ink leading-relaxed">{value}</p>}
    </div>
  );
}

function KPI({ value, label }) {
  return (
    <div className="bg-gradient-to-br from-[#0f172a] to-[#1e293b] text-white rounded-xl px-4 py-3 text-center">
      <p className="text-xl font-extrabold">{value}</p>
      <p className="text-[10px] text-blue-200 mt-0.5">{label}</p>
    </div>
  );
}

function SectionsStatus({ mandatory, errors }) {
  if (!mandatory || mandatory.length === 0) return null;
  const missing = new Set(
    (errors || []).filter((e) => e.error_type === "missing_required_section").map((e) => e.text),
  );

  return (
    <div className="border border-line bg-panel-muted rounded-xl p-4">
      <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-2">Required Sections</p>
      <div className="flex flex-wrap gap-2">
        {mandatory.map((s) => {
          const ok = !missing.has(s);
          return (
            <span
              key={s}
              className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                ok ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"
              }`}
            >
              {ok ? "✓" : "✗"} {s}
            </span>
          );
        })}
      </div>
    </div>
  );
}

function ReferenceAnalysis({ data }) {
  const s = data.summary || {};
  const entries = data.entries || [];
  const passed = s.checks_passed || [];
  const failed = s.checks_failed || [];

  return (
    <div className="border border-line rounded-xl p-4 space-y-3">
      <h3 className="text-sm font-bold border-b border-line pb-2">Reference Quality Analysis</h3>

      {/* Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <MiniStat val={s.total || 0} label="References" />
        <MiniStat val={s.parsed_ok || 0} label="Parsed OK" />
        <MiniStat val={s.total_issues || 0} label="Issues" warn={s.total_issues > 0} />
        <MiniStat val={s.style || "?"} label="Style" />
      </div>

      {/* Checks chips */}
      <div className="flex flex-wrap gap-1.5">
        {passed.map((c) => (
          <span key={c} className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-green-50 text-green-700">
            ✓ {c}
          </span>
        ))}
        {failed.map((c) => (
          <span key={c} className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-red-50 text-red-700">
            ✗ {c}
          </span>
        ))}
      </div>

      {/* List issues */}
      {data.list_level_issues?.length > 0 && (
        <div className="border border-orange-200 bg-orange-50 rounded-lg p-3 text-sm space-y-1">
          <p className="font-semibold text-orange-800 text-xs">List-level issues</p>
          {data.list_level_issues.map((iss, i) => (
            <p key={i} className="text-xs text-orange-900">
              <strong>[{iss.position}]</strong> {iss.detail || iss.check}
              {iss.expected && (
                <span className="text-gray-500 ml-1">
                  Expected: <code className="bg-gray-100 px-1 rounded text-[10px]">{iss.expected}</code>
                </span>
              )}
            </p>
          ))}
        </div>
      )}

      {/* Entries */}
      {entries.length > 0 && (
        <div className="space-y-1.5">
          {entries.map((entry) => {
            const issues = entry.issues || [];
            const parsed = entry.parsed || {};
            return (
              <details
                key={entry.id}
                className={`border rounded-lg overflow-hidden ${
                  issues.length ? "border-l-4 border-l-orange-400 border-gray-200" : "border-l-4 border-l-green-400 border-gray-200"
                }`}
              >
                <summary className="flex items-center gap-2 px-3 py-2 bg-panel-muted cursor-pointer text-xs select-none list-none [&::-webkit-details-marker]:hidden">
                  <span>{issues.length ? "⚠" : "✓"}</span>
                  <span className="font-bold text-gray-600 w-10">{entry.id}</span>
                  <span className="flex-1 truncate text-gray-700">
                    {(parsed.title || entry.raw_text || "").substring(0, 80)}
                  </span>
                  <span
                    className={`shrink-0 px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                      issues.length
                        ? "bg-orange-100 text-orange-700"
                        : "bg-gray-100 text-gray-500"
                    }`}
                  >
                    {issues.length ? `${issues.length} issue${issues.length > 1 ? "s" : ""}` : "OK"}
                  </span>
                </summary>
                <div className="px-3 py-2 text-xs space-y-1 bg-white">
                  {entry.raw_text && (
                    <p className="text-gray-500">
                      <strong>Raw:</strong> <em>{entry.raw_text}</em>
                    </p>
                  )}
                  {parsed.authors?.length > 0 && <p>Authors: {parsed.authors.join(", ")}</p>}
                  {parsed.pub_date && <p>Year: {parsed.pub_date}</p>}
                  {parsed.doi && (
                    <p>
                      DOI:{" "}
                      <a
                        href={`https://doi.org/${parsed.doi}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-brand underline"
                      >
                        {parsed.doi}
                      </a>
                    </p>
                  )}
                  {issues.length > 0 && (
                    <ul className="space-y-1 mt-1">
                      {issues.map((iss, j) => (
                        <li
                          key={j}
                          className="border border-orange-200 bg-orange-50/50 rounded-md px-2 py-1.5 flex flex-wrap gap-1.5 items-baseline"
                        >
                          <span className="text-[10px] font-bold uppercase bg-orange-100 text-orange-700 rounded px-1.5 py-0.5">
                            {iss.check}
                          </span>
                          {iss.field && <span className="text-[10px] text-gray-400">{iss.field}</span>}
                          <span className="flex-1 text-gray-700">{iss.detail}</span>
                          {iss.suggestion && (
                            <span className="w-full text-[11px] bg-blue-50 text-blue-700 rounded px-2 py-1 mt-0.5">
                              {iss.suggestion}
                            </span>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                  {issues.length === 0 && (
                    <p className="text-green-700 font-semibold">No issues found.</p>
                  )}
                </div>
              </details>
            );
          })}
        </div>
      )}
    </div>
  );
}

function MiniStat({ val, label, warn }) {
  return (
    <div className="border border-line rounded-lg bg-panel-muted px-3 py-2 text-center">
      <p className={`text-base font-bold ${warn ? "text-red-600" : "text-ink"}`}>{val}</p>
      <p className="text-[10px] text-gray-400 uppercase tracking-wide">{label}</p>
    </div>
  );
}
