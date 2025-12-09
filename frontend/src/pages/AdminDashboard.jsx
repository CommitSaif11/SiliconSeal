// src/pages/AdminDashboard.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api/v1";

export default function AdminDashboard() {
  const [kbEntries, setKbEntries] = useState([]);
  const [loadingKB, setLoadingKB] = useState(true);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  // Scraper multi-part
  const [partsText, setPartsText] = useState("");
  const [attempts, setAttempts] = useState(1);
  const [running, setRunning] = useState(false);
  const [scrapeResults, setScrapeResults] = useState([]);

  // Local histories
  const [batchHistory, setBatchHistory] = useState([]);
  const [singleHistory, setSingleHistory] = useState([]);
  const [scrapeHistory, setScrapeHistory] = useState([]);

  // Admin Logs (human-readable)
  const [logs, setLogs] = useState([]);
  const [logsLoading, setLogsLoading] = useState(false);
  const [logsError, setLogsError] = useState("");
  const [logsPage, setLogsPage] = useState(1);
  const [logsPageSize, setLogsPageSize] = useState(10);
  const [logsTotal, setLogsTotal] = useState(0);
  const [logFilters, setLogFilters] = useState({
    part_id: "",
    verdict: "",
    algorithm: "",
    requires_review: "",
  });

  useEffect(() => {
    loadKB();
    try {
      setBatchHistory(JSON.parse(localStorage.getItem("batch_history") || "[]"));
    } catch {
      setBatchHistory([]);
    }
    try {
      setSingleHistory(JSON.parse(localStorage.getItem("single_history") || "[]"));
    } catch {
      setSingleHistory([]);
    }
    try {
      setScrapeHistory(JSON.parse(localStorage.getItem("scrape_history") || "[]"));
    } catch {
      setScrapeHistory([]);
    }
    loadLogs(1, logsPageSize, logFilters);
    // eslint-disable-next-line
  }, []);

  const loadKB = async () => {
    setLoadingKB(true);
    setError("");
    try {
      const res = await axios.get(`${API_BASE}/kb`);
      setKbEntries(res.data?.entries || []);
    } catch (err) {
      console.error(err);
      setError("Failed to load KB entries.");
    } finally {
      setLoadingKB(false);
    }
  };

  const handleReloadKB = async () => {
    setError("");
    setInfo("");
    try {
      const res = await axios.post(`${API_BASE}/admin/reload-kb`);
      setInfo(`Reloaded KB (count: ${res.data?.count ?? "?"})`);
      await loadKB();
    } catch (err) {
      console.error(err);
      setError("KB reload failed.");
    }
  };

  const persistScrapeHistory = (entry) => {
    try {
      const hist = JSON.parse(localStorage.getItem("scrape_history") || "[]");
      hist.unshift(entry);
      localStorage.setItem("scrape_history", JSON.stringify(hist.slice(0, 100)));
      setScrapeHistory(JSON.parse(localStorage.getItem("scrape_history") || "[]"));
    } catch {
      // ignore
    }
  };

  // Multi-part scraping with retries
  const handleRunScraper = async () => {
    setError("");
    setInfo("");
    setScrapeResults([]);

    const parts = partsText
      .split(/[\n,]+/)
      .map((p) => p.trim())
      .filter(Boolean);

    if (parts.length === 0) {
      setError("Enter at least one part id.");
      return;
    }
    if (!Number.isInteger(Number(attempts)) || attempts < 1) {
      setError("Attempts must be integer >= 1.");
      return;
    }

    setRunning(true);
    const results = [];

    for (const part of parts) {
      const row = { part, status: "pending", attempts: 0, response: null };
      results.push(row);
      setScrapeResults([...results]);

      let ok = false;
      let lastResp = null;

      for (let i = 1; i <= attempts; i++) {
        row.attempts = i;
        setScrapeResults([...results]);

        try {
          const res = await axios.post(
            `${API_BASE}/admin/kb/enrich-and-save?part=${encodeURIComponent(part)}`
          );
          row.status = "success";
          row.response = res.data;
          ok = true;

          persistScrapeHistory({
            id: Date.now(),
            part,
            op: res.data?.operation,
            saved_part_id: res.data?.saved_part_id,
            raw: res.data,
            ts: new Date().toISOString(),
          });

          break;
        } catch (err) {
          lastResp = err?.response?.data || err?.message || "error";
          row.status = "retrying";
          row.response = lastResp;
        }
      }

      if (!ok) {
        row.status = "failed";
        row.response = lastResp;
      }

      setScrapeResults([...results]);
    }

    try {
      await loadKB();
    } catch {
      // ignore
    }

    setRunning(false);
    setInfo("Scrape run finished.");
  };

  // =========================
  // Admin Logs Loader
  // =========================
  async function loadLogs(page = 1, page_size = logsPageSize, filters = logFilters) {
    setLogsLoading(true);
    setLogsError("");
    try {
      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("page_size", String(page_size));
      if (filters.part_id?.trim()) params.set("part_id", filters.part_id.trim());
      if (filters.verdict?.trim()) params.set("verdict", filters.verdict.trim());
      if (filters.algorithm?.trim()) params.set("algorithm", filters.algorithm.trim());
      if (filters.requires_review === "true") params.set("requires_review", "true");
      if (filters.requires_review === "false") params.set("requires_review", "false");

      const url = `${API_BASE}/admin/logs?${params.toString()}`;
      const res = await axios.get(url);

      if (!res?.data || !Array.isArray(res.data?.data)) {
        throw new Error("Unexpected logs response");
      }

      setLogs(res.data.data);
      setLogsTotal(Number(res.data?.total || 0));
      setLogsPage(page);
      setLogsPageSize(page_size);
    } catch (err) {
      console.error("Load logs error:", err);
      setLogs([]);
      setLogsTotal(0);
      // If endpoint not found or not yet added, show gentle hint
      setLogsError("Could not load verification logs. Ensure /api/v1/admin/logs is available.");
    } finally {
      setLogsLoading(false);
    }
  }

  const verdictBadge = (v0) => {
    const v = (v0 || "").toUpperCase();
    if (v === "GENUINE") return <span className="text-green-400">✔ Genuine</span>;
    if (v === "FAKE") return <span className="text-red-400">✘ Counterfeit</span>;
    if (v === "UNCERTAIN") return <span className="text-amber-400">⚠ Uncertain</span>;
    if (v === "MULTIPLE_CANDIDATES") return <span className="text-blue-400">ℹ Multiple Candidates</span>;
    return <span className="text-gray-400">Unknown</span>;
  };

  const pct = (val) => {
    if (typeof val !== "number") return "-";
    return `${(val * 100).toFixed(2)}%`;
  };

  const pctPlain = (val) => {
    if (typeof val !== "number") return "-";
    return `${Number(val).toFixed(2)}%`;
  };

  const hasNext = logsPage * logsPageSize < logsTotal;

  return (
    <section>
      <h1 className="page-title">Admin Dashboard</h1>

      {/* NEW BUTTON — Damaged IC Inspection */}
      <div className="mb-4">
        <button
          onClick={() => (window.location.href = "/admin/damaged-ic")}
          className="btn-primary"
        >
          Damaged IC Inspection
        </button>
      </div>

      <div className="card mb-4">
        <div className="flex gap-3 flex-wrap">
          <button className="btn-primary" onClick={handleReloadKB}>
            Reload KB
          </button>
          <div className="text-xs text-gray-500 self-center">
            Admin actions (UI-only)
          </div>
        </div>

        {error && <p className="text-red-500 mt-2">{error}</p>}
        {info && <p className="text-green-500 mt-2">{info}</p>}
      </div>

      {/* Scraper */}
      <div className="card mb-4">
        <h2 className="section-title">Bulk Scraper (frontend loop)</h2>
        <p className="text-xs text-gray-500 mb-2">
          Paste parts (newline or comma separated). Set attempts. Frontend will
          call /admin/kb/enrich-and-save for each part.
        </p>

        <textarea
          rows={3}
          className="input"
          placeholder={`STM32F030C8T6
ATMEGA328P`}
          value={partsText}
          onChange={(e) => setPartsText(e.target.value)}
        />

        <div className="grid md:grid-cols-3 gap-3 mt-3 items-end">
          <div>
            <label className="text-sm">Attempts (N)</label>
            <input
              className="input"
              type="number"
              min={1}
              value={attempts}
              onChange={(e) => setAttempts(Number(e.target.value))}
            />
          </div>

          <div>
            <button
              className="btn-primary"
              onClick={handleRunScraper}
              disabled={running}
            >
              {running ? "Running…" : "Run Scraper"}
            </button>
          </div>

          <div className="text-xs text-gray-500">
            Scrape history: {scrapeHistory.length} entries • Batch history:{" "}
            {(() => {
              try {
                return JSON.parse(localStorage.getItem("batch_history") || "[]").length;
              } catch {
                return 0;
              }
            })()}
          </div>
        </div>

        {scrapeResults.length > 0 && (
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Run Results</h3>
            <div className="space-y-2">
              {scrapeResults.map((r, i) => (
                <div key={i} className="p-3 border rounded dark:border-gray-700">
                  <div className="flex justify-between">
                    <div>
                      <b>{r.part}</b> — {r.status}
                    </div>
                    <div className="text-xs">tries: {r.attempts}</div>
                  </div>
                  <pre className="mt-2 text-xs bg-gray-100 dark:bg-gray-900 p-2 rounded overflow-auto">
                    {JSON.stringify(r.response, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* KB table */}
      <div className="card mb-4">
        <h2 className="section-title">
          Knowledge Base Entries ({kbEntries.length})
        </h2>
        {loadingKB ? (
          <p>Loading...</p>
        ) : (
          <div className="overflow-auto">
            <table className="table-base">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Part ID</th>
                  <th>OEM</th>
                  <th>Package</th>
                </tr>
              </thead>
              <tbody>
                {kbEntries.map((e, i) => (
                  <tr key={i} className="table-row-hover">
                    <td>{i + 1}</td>
                    <td className="font-mono">{e.part_id}</td>
                    <td>{e.oem || e.manufacturer || "-"}</td>
                    <td>{e.package || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Histories */}
      <div className="grid md:grid-cols-3 gap-4">
        {/* Batch history */}
        <div className="card">
          <h3 className="section-title">Recent Batches</h3>
          {batchHistory.length === 0 ? (
            <p className="text-sm">No batches yet.</p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-auto">
              {batchHistory.map((b, idx) => {
                const filesCount =
                  (Array.isArray(b.previews) && b.previews.length) ||
                  (Array.isArray(b.raw?.results) && b.raw.results.length) ||
                  0;
                return (
                  <div key={idx} className="p-2 border rounded dark:border-gray-700">
                    <div className="flex justify-between">
                      <div>
                        <b>Batch #{idx + 1}</b>
                      </div>
                      <div className="text-xs">
                        {b.timestamp ? new Date(b.timestamp).toLocaleString() : "-"}
                      </div>
                    </div>
                    <div className="text-xs mt-1">
                      Part: {b.partId || "(auto)"} • Files: {filesCount}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Single scans */}
        <div className="card">
          <h3 className="section-title">Recent Single Scans</h3>
          {singleHistory.length === 0 ? (
            <p className="text-sm">No single scans yet.</p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-auto">
              {singleHistory.map((s, i) => (
                <div
                  key={i}
                  className="flex gap-2 items-center p-2 border rounded dark:border-gray-700"
                >
                  {s.preview ? (
                    <img
                      src={s.preview}
                      alt=""
                      className="w-12 h-8 object-cover rounded"
                    />
                  ) : (
                    <div className="w-12 h-8 bg-gray-800 rounded" />
                  )}
                  <div className="text-xs">
                    <div>
                      <b>{s.filename || "Scan"}</b>
                    </div>
                    <div className="text-xs">
                      {s.timestamp ? new Date(s.timestamp).toLocaleString() : "-"}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Scrape history */}
        <div className="card">
          <h3 className="section-title">Scrape History</h3>
          {scrapeHistory.length === 0 ? (
            <p className="text-sm">No scrapes yet.</p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-auto">
              {scrapeHistory.map((h, i) => (
                <div
                  key={i}
                  className="p-2 border rounded dark:border-gray-700"
                >
                  <div className="flex justify-between">
                    <div>{h.part}</div>
                    <div className="text-xs">
                      {h.ts ? new Date(h.ts).toLocaleString() : "-"}
                    </div>
                  </div>
                  <div className="text-xs">
                    Op: {h.op} • Saved: {h.saved_part_id}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Verification Logs */}
      <div className="card mt-6">
        <div className="flex justify-between items-center">
          <h2 className="section-title">Verification Logs</h2>
          <button
            className="btn-secondary"
            onClick={() => loadLogs(logsPage, logsPageSize, logFilters)}
            disabled={logsLoading}
          >
            {logsLoading ? "Refreshing…" : "Refresh"}
          </button>
        </div>

        {/* Filters */}
        <div className="grid md:grid-cols-5 gap-3 mt-3">
          <input
            className="input"
            placeholder="Part ID"
            value={logFilters.part_id}
            onChange={(e) => setLogFilters({ ...logFilters, part_id: e.target.value })}
          />
          <select
            className="input"
            value={logFilters.verdict}
            onChange={(e) => setLogFilters({ ...logFilters, verdict: e.target.value })}
          >
            <option value="">Verdict (all)</option>
            <option value="GENUINE">GENUINE</option>
            <option value="FAKE">FAKE</option>
            <option value="UNCERTAIN">UNCERTAIN</option>
            <option value="MULTIPLE_CANDIDATES">MULTIPLE_CANDIDATES</option>
          </select>
          <select
            className="input"
            value={logFilters.algorithm}
            onChange={(e) => setLogFilters({ ...logFilters, algorithm: e.target.value })}
          >
            <option value="">Algorithm (all)</option>
            <option value="regex">regex</option>
            <option value="aho_corasick">aho_corasick</option>
          </select>
          <select
            className="input"
            value={logFilters.requires_review}
            onChange={(e) => setLogFilters({ ...logFilters, requires_review: e.target.value })}
          >
            <option value="">Requires Review (all)</option>
            <option value="true">Yes</option>
            <option value="false">No</option>
          </select>
          <div className="flex gap-2">
            <button
              className="btn-primary flex-1"
              onClick={() => loadLogs(1, logsPageSize, logFilters)}
              disabled={logsLoading}
            >
              Search
            </button>
            <button
              className="btn-secondary"
              onClick={() => {
                const cleared = { part_id: "", verdict: "", algorithm: "", requires_review: "" };
                setLogFilters(cleared);
                loadLogs(1, logsPageSize, cleared);
              }}
              disabled={logsLoading}
            >
              Clear
            </button>
          </div>
        </div>

        {/* Logs list */}
        {logsError && <p className="text-red-500 mt-3">{logsError}</p>}

        {!logsError && (
          <>
            {logs.length === 0 && !logsLoading ? (
              <div className="text-sm text-gray-500 mt-4">No logs found.</div>
            ) : null}

            <div className="space-y-3 mt-4">
              {logs.map((L, i) => (
                <div key={i} className="p-3 border rounded dark:border-gray-700">
                  <div className="flex justify-between items-center">
                    <div className="flex gap-2 items-center">
                      <div className="text-sm">{verdictBadge(L.verdict)}</div>
                      <div className="text-xs text-gray-400">
                        Accuracy: {pct(L.overall_confidence)} · OCR: {pct(L.ocr_confidence_percent ? L.ocr_confidence_percent / 100 : null)}
                      </div>
                    </div>
                    <div className="text-xs text-gray-400">
                      {L.timestamp_iso ? new Date(L.timestamp_iso).toLocaleString() : "-"}
                    </div>
                  </div>

                  <div className="text-xs text-gray-300 mt-1">
                    Part: <span className="font-mono">{L.part_id || "-"}</span> · Algorithm: {L.algorithm || "-"} · Risk: {L.risk_level || "-"}
                  </div>

                  {/* Summary and key points */}
                  <div className="mt-2 text-sm">
                    <div className="font-semibold">Summary</div>
                    <div className="text-gray-200">{L.summary || "-"}</div>
                  </div>

                  {Array.isArray(L.key_points) && L.key_points.length > 0 && (
                    <div className="mt-2">
                      <div className="font-semibold text-sm">Key Points</div>
                      <ul className="list-disc ml-5 text-xs">
                        {L.key_points.map((p, idx) => (
                          <li key={idx}>{p}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="mt-2 text-xs">
                    <div className="font-semibold">Checks Summary</div>
                    <div>{L.matches_summary || "-"}</div>
                  </div>

                  <div className="mt-2 text-xs">
                    <div className="font-semibold">OEM</div>
                    <div>{L.oem_summary || "-"}</div>
                  </div>

                  <div className="mt-2 text-xs">
                    <div className="font-semibold">Flags</div>
                    <div>{Array.isArray(L.flags) && L.flags.length ? L.flags.join(" · ") : "-"}</div>
                  </div>

                  {/* Raw JSON */}
                  <details className="mt-2">
                    <summary className="text-blue-400 cursor-pointer text-sm">View Raw</summary>
                    <pre className="bg-gray-900 p-2 rounded text-xs overflow-auto mt-1">
                      {JSON.stringify(L.raw ?? L, null, 2)}
                    </pre>
                  </details>
                </div>
              ))}
            </div>

            {/* Pagination */}
            <div className="flex justify-between items-center mt-4">
              <div className="text-xs text-gray-400">
                Total: {logsTotal} · Page: {logsPage} · Size: {logsPageSize} · {hasNext ? "More pages available" : "End"}
              </div>
              <div className="flex gap-2">
                <button
                  className="btn-secondary"
                  onClick={() => loadLogs(Math.max(1, logsPage - 1), logsPageSize, logFilters)}
                  disabled={logsLoading || logsPage <= 1}
                >
                  Prev
                </button>
                <button
                  className="btn-secondary"
                  onClick={() => loadLogs(logsPage + 1, logsPageSize, logFilters)}
                  disabled={logsLoading || !hasNext}
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </section>
  );
}