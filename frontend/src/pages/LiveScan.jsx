import React, { useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

export default function LiveScan() {
  const [frame, setFrame] = useState("");
  const [partId, setPartId] = useState("");
  const [algorithm, setAlgorithm] = useState("aho_corasick");
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!frame.trim()) return setError("Please paste Base64 frame");

    const formData = new FormData();
    formData.append("frame", frame.trim());
    if (partId) formData.append("part_id", partId);
    formData.append("algorithm", algorithm);

    try {
      setSubmitting(true);
      const res = await axios.post(`${API_BASE}/scan/frame`, formData);
      setResult(res.data);
    } catch (err) {
      setError("Live scan failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section>
      <h1 className="page-title">Live Frame Scan</h1>

      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea
            rows={4}
            value={frame}
            onChange={(e) => setFrame(e.target.value)}
            placeholder="Paste Base64 frame here..."
            className="input h-32"
          />

          <div className="grid md:grid-cols-2 gap-4">
            <input value={partId} onChange={(e)=>setPartId(e.target.value)} placeholder="Part ID (optional)" className="input" />

            <select value={algorithm} onChange={(e)=>setAlgorithm(e.target.value)} className="input">
              <option value="aho_corasick">Aho–Corasick</option>
              <option value="regex">Regex</option>
            </select>
          </div>

          {error && <p className="text-red-500">{error}</p>}

          <button className="btn-primary">{submitting ? "Scanning…" : "Send Frame"}</button>
        </form>
      </div>

      {result && (
        <div className="card mt-6">
          <h2 className="section-title">Live Scan Result</h2>
          <pre className="bg-gray-100 dark:bg-gray-900 p-3 rounded text-xs overflow-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </section>
  );
}
