import React, { useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

function BatchScan() {
  const [files, setFiles] = useState([]);
  const [partId, setPartId] = useState("");
  const [algorithm, setAlgorithm] = useState("regex");
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!files.length) {
      setError("Please select at least one image.");
      return;
    }
    if (!partId) {
      setError("Part ID is required for batch scan.");
      return;
    }

    const formData = new FormData();
    Array.from(files).forEach((file) => formData.append("files", file));
    formData.append("part_id", partId);
    formData.append("algorithm", algorithm);

    try {
      setSubmitting(true);
      const res = await axios.post(`${API_BASE}/scan/batch`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError("Batch scan failed – check backend logs.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section>
      <h1 className="text-2xl font-bold mb-4">Batch Scan</h1>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6"
      >
        <div>
          <label className="block text-sm font-medium mb-1">
            IC Images (multiple)
          </label>
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={(e) => setFiles(e.target.files ? [...e.target.files] : [])}
            className="block w-full text-sm file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700 border border-gray-300 rounded-md bg-white dark:bg-gray-900 dark:border-gray-700"
          />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium mb-1">Part ID</label>
            <input
              type="text"
              value={partId}
              onChange={(e) => setPartId(e.target.value)}
              className="w-full text-sm border border-gray-300 rounded-md px-2 py-1.5 bg-white dark:bg-gray-900 dark:border-gray-700"
              placeholder="e.g. stm32f030c8t6"
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
              <option value="regex">Regex</option>
              <option value="aho_corasick">Aho–Corasick</option>
            </select>
          </div>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="px-4 py-2 rounded-md bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed transition-transform transform hover:-translate-y-0.5"
        >
          {submitting ? "Scanning Batch…" : "Upload & Scan Batch"}
        </button>
      </form>

      {result && (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6 text-sm">
          <h2 className="font-semibold mb-2">Batch Scan Result (Raw JSON)</h2>
          <pre className="bg-gray-100 dark:bg-gray-900 rounded p-3 overflow-auto text-xs">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </section>
  );
}

export default BatchScan;
