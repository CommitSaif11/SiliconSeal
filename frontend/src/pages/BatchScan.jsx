// src/pages/BatchScan.jsx
import React, { useState } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api/v1";

export default function BatchScan() {
  const [files, setFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [partId, setPartId] = useState(""); // Optional
  const [algorithm, setAlgorithm] = useState("regex");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFiles = (e) => {
    const arr = Array.from(e.target.files || []);
    setFiles(arr);
    setPreviews(arr.map((f) => ({ name: f.name, url: URL.createObjectURL(f) })));
  };

  const saveHistory = (entry) => {
    try {
      const hist = JSON.parse(localStorage.getItem("batch_history") || "[]");
      hist.unshift(entry);
      localStorage.setItem("batch_history", JSON.stringify(hist.slice(0, 50)));
    } catch {
      // ignore localStorage errors
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!files.length) {
      alert("Select at least one image");
      return;
    }

    const form = new FormData();
    files.forEach((f) => form.append("files", f));
    // Part ID is optional — only append when provided
    if (partId && partId.trim().length > 0) {
      form.append("part_id", partId.trim());
    }
    form.append("algorithm", algorithm);

    try {
      setLoading(true);
      const res = await axios.post(`${API_BASE}/scan/batch`, form);
      // Validate shape
      if (!res?.data || !Array.isArray(res.data.results)) {
        console.error("Unexpected API response:", res?.data);
        alert("Unexpected API response shape");
        return;
      }

      const payload = {
        timestamp: new Date().toISOString(),
        previews,
        raw: res.data,
      };

      setResults(payload);
      saveHistory(payload);
    } catch (err) {
      console.error("Batch scan error:", err);
      alert("Batch scan failed.");
    } finally {
      setLoading(false);
    }
  };

  const renderVerdictBadge = (verdict) => {
    const v = (verdict || "").toUpperCase();
    if (v === "GENUINE") return <span className="text-green-400">✔ Genuine Marking</span>;
    if (v === "FAKE") return <span className="text-red-400">✘ Counterfeit / Not Genuine</span>;
    if (v === "UNCERTAIN") return <span className="text-amber-400">⚠ Uncertain — Requires Manual Inspection</span>;
    if (v === "MULTIPLE_CANDIDATES") return <span className="text-blue-400">ℹ Multiple Candidates Detected</span>;
    return <span className="text-gray-400">Result Unknown</span>;
  };

  const formatPct = (val) => {
    if (typeof val !== "number") return "-";
    return `${(val * 100).toFixed(2)}%`;
  };

  const summarizeChecks = (matches) => {
    if (!matches || typeof matches !== "object") return "No structured checks";
    const keys = Object.keys(matches);
    const total = keys.length;
    const ok = keys.filter((k) => !!matches[k]).length;
    const failed = keys.filter((k) => !matches[k]);
    return `${ok}/${total} checks matched${failed.length ? ` (missed: ${failed.join(", ")})` : ""}`;
  };

  const oemSummary = (oem_info) => {
    if (!oem_info || typeof oem_info !== "object") return "-";
    const oem = oem_info.oem;
    const pn = oem_info.part_number;
    return oem && pn ? `${oem} — ${pn}` : oem || pn || "-";
  };

  return (
    <section>
      <h1 className="page-title">Batch Scan</h1>

      {/* Upload Form */}
      <div className="card mb-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="font-semibold text-sm">IC Images (multiple)</label>
            <input
              type="file"
              multiple
              accept="image/*"
              onChange={handleFiles}
              className="file-input"
            />
          </div>

          {previews.length > 0 && (
            <div className="grid grid-cols-6 gap-3">
              {previews.map((p, i) => (
                <div key={i} className="p-1 border rounded bg-gray-800/40">
                  <img src={p.url} className="h-20 object-cover w-full rounded" alt={p.name} />
                  <p className="text-xs truncate">{p.name}</p>
                </div>
              ))}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <input
              className="input"
              placeholder="Part ID (optional)"
              value={partId}
              onChange={(e) => setPartId(e.target.value)}
            />
            <select
              className="input"
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value)}
            >
              <option value="regex">Regex</option>
              <option value="aho_corasick">Aho–Corasick</option>
            </select>
          </div>

          <button className="btn-primary" disabled={loading}>
            {loading ? "Scanning..." : "Upload & Scan Batch"}
          </button>
        </form>
      </div>

      {/* RESULTS */}
      {results ? (
        <div className="space-y-6">
          <h2 className="section-title">Batch Results</h2>

          {Array.isArray(results.raw?.results) && results.raw.results.length ? (
            results.raw.results.map((r, idx) => {
              const preview = results.previews?.[idx];

              return (
                <div key={idx} className="card result-box flex flex-col md:flex-row gap-4 p-4">
                  {/* Left image */}
                  <div className="w-full md:w-40">
                    {preview?.url ? (
                      <img
                        src={preview.url}
                        className="w-full h-28 object-cover rounded"
                        alt={preview?.name || `preview-${idx}`}
                      />
                    ) : (
                      <div className="w-full h-28 bg-gray-800 rounded" />
                    )}
                    <p className="text-xs mt-1 truncate">{preview?.name || "-"}</p>
                  </div>

                  {/* Right side */}
                  <div className="flex-1">
                    {/* Verdict */}
                    <div className="text-lg font-bold">
                      {renderVerdictBadge(r?.verdict)}
                    </div>

                    {/* Meta line */}
                    <div className="mt-1 text-xs text-gray-400">
                      Algorithm: {r?.algorithm_used || "-"} · Accuracy: {formatPct(r?.confidence_score)} · OCR: {formatPct(r?.ocr_confidence)}
                    </div>

                    {/* Extracted Text / OCR */}
                    <div className="mt-3">
                      <div className="font-semibold text-gray-300 text-sm">Extracted Text</div>
                      <div className="bg-gray-800 p-2 rounded text-xs">
                        {r?.ocr_text?.length
                          ? r.ocr_text
                          : [
                              r?.extracted_fields?.part_code,
                              r?.extracted_fields?.date_code,
                              r?.extracted_fields?.lot_code,
                            ].filter(Boolean).join(" ") || "-"}
                      </div>
                    </div>

                    {/* Checks Summary */}
                    <div className="mt-3">
                      <div className="font-semibold text-gray-300 text-sm">Checks Summary</div>
                      <div className="text-xs text-gray-200">
                        {summarizeChecks(r?.matches)}
                      </div>
                    </div>

                    {/* OEM Summary */}
                    <div className="mt-3">
                      <div className="font-semibold text-gray-300 text-sm">OEM & Part</div>
                      <div className="text-xs text-gray-200">
                        {oemSummary(r?.oem_info)}
                      </div>
                    </div>

                    {/* Flags */}
                    {Array.isArray(r?.flags) && r.flags.length > 0 && (
                      <div className="mt-3">
                        <div className="font-semibold text-gray-300 text-sm">Flags</div>
                        <div className="text-xs text-gray-200">{r.flags.join(" · ")}</div>
                      </div>
                    )}

                    {/* Requires Review */}
                    <div className="mt-3">
                      <div className="font-semibold text-gray-300 text-sm">Requires Admin Review</div>
                      <div className="text-xs text-gray-200">{r?.requires_admin_review ? "Yes" : "No"}</div>
                    </div>

                    {/* Expand Raw JSON */}
                    <details className="mt-3">
                      <summary className="text-blue-400 cursor-pointer text-sm">
                        View Raw Data
                      </summary>
                      <pre className="bg-gray-900 mt-2 p-3 rounded text-xs overflow-auto">
                        {JSON.stringify(r ?? {}, null, 2)}
                      </pre>
                    </details>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="card result-box text-gray-500 text-center py-10">
              No batch results available.
            </div>
          )}
        </div>
      ) : (
        <div className="card result-box text-gray-500 text-center py-10">
          Batch results will appear here.
        </div>
      )}
    </section>
  );
}