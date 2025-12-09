// src/pages/Scan.jsx
import React, { useState } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api/v1";

export default function Scan() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [partId, setPartId] = useState(""); // Optional
  const [algorithm, setAlgorithm] = useState("aho_corasick");
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleFile = (e) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setPreview(URL.createObjectURL(f));
    } else {
      setFile(null);
      setPreview("");
    }
  };

  const saveHistory = (entry) => {
    try {
      const hist = JSON.parse(localStorage.getItem("single_history") || "[]");
      hist.unshift(entry);
      localStorage.setItem("single_history", JSON.stringify(hist.slice(0, 50)));
    } catch {
      // ignore localStorage errors
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!file) {
      setError("Please select an image.");
      return;
    }

    const form = new FormData();
    form.append("file", file);
    // Part ID is optional — only append if provided
    if (partId && partId.trim().length > 0) {
      form.append("part_id", partId.trim());
    }
    form.append("algorithm", algorithm);

    try {
      setSubmitting(true);
      const res = await axios.post(`${API_BASE}/scan`, form);
      if (!res?.data || typeof res.data !== "object") {
        console.error("Unexpected API response:", res?.data);
        setError("Unexpected API response shape.");
        return;
    }

      const formatted = {
        filename: file.name,
        preview,
        partId,
        algorithm,
        timestamp: new Date().toISOString(),
        raw: res.data, // VerificationResponse from backend
      };

      setResult(formatted);
      saveHistory(formatted);
    } catch (err) {
      console.error("Single scan error:", err);
      setError("Scan failed.");
    } finally {
      setSubmitting(false);
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

  const RawBlock = ({ data }) => (
    <pre className="bg-gray-900 p-3 rounded text-xs overflow-auto mt-2">
      {JSON.stringify(data ?? {}, null, 2)}
    </pre>
  );

  return (
    <section>
      <h1 className="page-title">Single Scan</h1>

      <div className="flex flex-col md:flex-row gap-6 items-start md:items-stretch">
        {/* LEFT SIDE */}
        <div className="card w-full md:w-1/2 flex flex-col justify-start">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium">IC Image</label>
              <input
                type="file"
                accept="image/*"
                onChange={handleFile}
                className="file-input"
              />
            </div>

            {preview && (
              <img
                src={preview}
                className="w-48 rounded border dark:border-gray-700 mt-2"
                alt="preview"
              />
            )}

            <div className="grid grid-cols-2 gap-4">
              <input
                value={partId}
                onChange={(e) => setPartId(e.target.value)}
                className="input"
                placeholder="Part ID (optional)"
              />
              <select
                value={algorithm}
                onChange={(e) => setAlgorithm(e.target.value)}
                className="input"
              >
                <option value="aho_corasick">Aho–Corasick</option>
                <option value="regex">Regex</option>
              </select>
            </div>

            {error && <p className="text-red-500">{error}</p>}

            <button className="btn-primary" disabled={submitting}>
              {submitting ? "Scanning…" : "Upload & Scan"}
            </button>
          </form>
        </div>

        {/* RIGHT SIDE — RESULT BOX */}
        <div className="card result-box w-full md:w-1/2 flex flex-col">
          {result ? (
            <>
              <h2 className="section-title">Analysis Result</h2>

              {/* Verdict */}
              <div className="text-lg font-bold mt-1">
                {renderVerdictBadge(result.raw?.verdict)}
              </div>

              <p className="text-xs text-gray-400">
                {new Date(result.timestamp).toLocaleString()}
              </p>

              <hr className="my-3 border-gray-600" />

              {/* Meta */}
              <div className="text-xs text-gray-400">
                Algorithm: {result.raw?.algorithm_used || "-"} · Accuracy: {formatPct(result.raw?.confidence_score)} · OCR: {formatPct(result.raw?.ocr_confidence)}
              </div>

              {/* Extracted Text */}
              <div className="mt-3">
                <div className="font-semibold text-gray-300 text-sm">Extracted Text</div>
                <div className="bg-gray-800 p-2 rounded text-xs">
                  {result.raw?.ocr_text?.length
                    ? result.raw.ocr_text
                    : [
                        result.raw?.extracted_fields?.part_code,
                        result.raw?.extracted_fields?.date_code,
                        result.raw?.extracted_fields?.lot_code,
                      ]
                        .filter(Boolean)
                        .join(" ") || "No text detected"}
                </div>
              </div>

              {/* Checks Summary */}
              <div className="mt-3">
                <div className="font-semibold text-gray-300 text-sm">Checks Summary</div>
                <div className="text-xs text-gray-200">
                  {summarizeChecks(result.raw?.matches)}
                </div>
              </div>

              {/* OEM Summary */}
              <div className="mt-3">
                <div className="font-semibold text-gray-300 text-sm">OEM & Part</div>
                <div className="text-xs text-gray-200">
                  {oemSummary(result.raw?.oem_info)}
                </div>
              </div>

              {/* Flags */}
              {Array.isArray(result.raw?.flags) && result.raw.flags.length > 0 && (
                <div className="mt-3">
                  <div className="font-semibold text-gray-300 text-sm">Flags</div>
                  <div className="text-xs text-gray-200">{result.raw.flags.join(" · ")}</div>
                </div>
              )}

              {/* Requires Review */}
              <div className="mt-3">
                <div className="font-semibold text-gray-300 text-sm">Requires Admin Review</div>
                <div className="text-xs text-gray-200">
                  {result.raw?.requires_admin_review ? "Yes" : "No"}
                </div>
              </div>

              {/* Candidate Parts */}
              {Array.isArray(result.raw?.candidate_parts) && result.raw.candidate_parts.length > 0 && (
                <div className="mt-3">
                  <div className="font-semibold text-gray-300 text-sm">Candidate Parts</div>
                  <ul className="list-disc ml-5 text-xs">
                    {result.raw.candidate_parts.map((c, i) => (
                      <li key={i}>{typeof c === "string" ? c : JSON.stringify(c)}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Expand Raw JSON */}
              <details className="mt-4">
                <summary className="text-blue-400 cursor-pointer text-sm">
                  View Raw Data
                </summary>
                <RawBlock data={result.raw} />
              </details>
            </>
          ) : (
            <div className="flex items-center justify-center text-gray-500 h-full">
              Result will appear here.
            </div>
          )}
        </div>
      </div>
    </section>
  );
}