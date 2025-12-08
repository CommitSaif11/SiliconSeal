import React, { useState } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api/v1";

export default function Scan() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [partId, setPartId] = useState("");
  const [algorithm, setAlgorithm] = useState("aho_corasick");
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleFile = (e) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setPreview(URL.createObjectURL(f));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!file) {
      setError("Please select an IC image.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    if (partId) formData.append("part_id", partId);
    formData.append("algorithm", algorithm);

    try {
      setSubmitting(true);
      const res = await axios.post(`${API_BASE}/scan`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError("Scan failed. Check backend logs.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section>
      <h1 className="text-3xl font-bold mb-4">Single IC Scan</h1>

      {/* Upload Box */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md">
        <form onSubmit={handleSubmit} className="space-y-4">

          {/* File Upload */}
          <div>
            <label className="block text-sm font-semibold mb-1">IC Image</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleFile}
              className="block w-full text-sm file:mr-3 file:py-1.5 file:px-3 file:bg-belBlue file:text-white file:rounded-md file:border-0 hover:file:bg-belBlueLight border border-gray-300 rounded-md dark:border-gray-700 dark:bg-gray-900"
            />
          </div>

          {/* Preview */}
          {preview && (
            <img
              src={preview}
              alt="preview"
              className="mt-3 w-48 rounded-lg shadow border border-gray-300 dark:border-gray-700"
            />
          )}

          {/* Inputs */}
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-1">Part ID (optional)</label>
              <input
                type="text"
                value={partId}
                onChange={(e) => setPartId(e.target.value)}
                className="w-full text-sm border border-gray-300 rounded-md px-2 py-1.5 dark:border-gray-700 dark:bg-gray-900"
                placeholder="e.g. stm32f030c8t6"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-1">Algorithm</label>
              <select
                value={algorithm}
                onChange={(e) => setAlgorithm(e.target.value)}
                className="w-full text-sm border border-gray-300 rounded-md px-2 py-1.5 dark:border-gray-700 dark:bg-gray-900"
              >
                <option value="aho_corasick">Aho–Corasick</option>
                <option value="regex">Regex</option>
              </select>
            </div>
          </div>

          {/* Error */}
          {error && <p className="text-red-500 text-sm">{error}</p>}

          {/* Submit */}
          <button
            type="submit"
            disabled={submitting}
            className="px-4 py-2 bg-belBlue text-white rounded-md hover:bg-belBlueLight transition disabled:opacity-50"
          >
            {submitting ? "Scanning…" : "Upload & Scan"}
          </button>
        </form>
      </div>

      {/* Results */}
      {result && (
        <div className="mt-6 bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md">
          <h2 className="font-semibold mb-2 text-lg">Scan Result</h2>
          <pre className="bg-gray-100 dark:bg-gray-900 p-3 rounded text-xs overflow-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </section>
  );
}
