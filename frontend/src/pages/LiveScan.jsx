import React, { useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

function LiveScan() {
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

    if (!frame.trim()) {
      setError("Please paste a Base64 image frame.");
      return;
    }

    const formData = new FormData();
    formData.append("frame", frame.trim());
    if (partId) formData.append("part_id", partId);
    formData.append("algorithm", algorithm);

    try {
      setSubmitting(true);
      const res = await axios.post(`${API_BASE}/scan/frame`, formData);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError("Live frame scan failed – check backend logs.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section>
      <h1 className="text-2xl font-bold mb-4">Live Frame Scan (Prototype)</h1>
      <p className="text-xs text-gray-500 mb-3">
        For now, paste a Base64-encoded image frame. Later we can attach a real
        webcam feed.
      </p>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6"
      >
        <div>
          <label className="block text-sm font-medium mb-1">
            Base64 Frame
          </label>
          <textarea
            value={frame}
            onChange={(e) => setFrame(e.target.value)}
            rows={4}
            className="w-full text-xs border border-gray-300 rounded-md px-2 py-1.5 bg-white dark:bg-gray-900 dark:border-gray-700"
            placeholder="Paste base64 image frame here…"
          />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium mb-1">
              Part ID (optional)
            </label>
            <input
              type="text"
              value={partId}
              onChange={(e) => setPartId(e.target.value)}
              className="w-full text-sm border border-gray-300 rounded-md px-2 py-1.5 bg-white dark:bg-gray-900 dark:border-gray-700"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">
              Algorithm
            </label>
            <select
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value)}
              className="w-full text-sm border border-gray-300 rounded-md px-2 py-1.5 bg-white dark:bg-gray-900 dark:border-gray-700"
            >
              <option value="aho_corasick">Aho–Corasick</option>
              <option value="regex">Regex</option>
            </select>
          </div>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="px-4 py-2 rounded-md bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed transition-transform transform hover:-translate-y-0.5"
        >
          {submitting ? "Scanning Frame…" : "Send Frame"}
        </button>
      </form>

      {result && (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6 text-sm">
          <h2 className="font-semibold mb-2">
            Live Frame Scan Result (Raw JSON)
          </h2>
          <pre className="bg-gray-100 dark:bg-gray-900 rounded p-3 overflow-auto text-xs">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </section>
  );
}

export default LiveScan;
