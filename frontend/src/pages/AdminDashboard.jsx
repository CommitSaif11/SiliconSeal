import React, { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

function AdminDashboard() {
  const [kbEntries, setKbEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reloadLoading, setReloadLoading] = useState(false);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  useEffect(() => {
    async function fetchKB() {
      try {
        setError("");
        const res = await axios.get(`${API_BASE}/kb`);
        setKbEntries(res.data.entries || []);
      } catch (err) {
        console.error(err);
        setError("Failed to load KB entries.");
      } finally {
        setLoading(false);
      }
    }
    fetchKB();
  }, []);

  const handleReload = async () => {
    try {
      setReloadLoading(true);
      setError("");
      setInfo("");
      const res = await axios.post(`${API_BASE}/admin/reload-kb`);
      setInfo(
        `KB reload triggered. Entries detected: ${res.data.count ?? "?"}`
      );
    } catch (err) {
      console.error(err);
      setError("KB reload failed.");
    } finally {
      setReloadLoading(false);
    }
  };

  return (
    <section>
      <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={handleReload}
          disabled={reloadLoading}
          className="px-3 py-1.5 rounded-md bg-blue-600 text-white text-xs sm:text-sm font-medium hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
        >
          {reloadLoading ? "Reloading KB…" : "Reload KB from JSON"}
        </button>

        <span className="text-xs text-gray-500">
          Admin mode is UI-only. Auth will be added in a later phase.
        </span>
      </div>

      {error && <p className="text-sm text-red-600 mb-2">{error}</p>}
      {info && <p className="text-sm text-green-600 mb-2">{info}</p>}

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 text-sm">
        <h2 className="font-semibold mb-2">
          Knowledge Base Entries ({kbEntries.length})
        </h2>

        {loading ? (
          <p className="text-gray-500">Loading KB entries…</p>
        ) : kbEntries.length === 0 ? (
          <p className="text-gray-500">No entries in KB yet.</p>
        ) : (
          <div className="overflow-auto">
            <table className="min-w-full text-xs sm:text-sm border-collapse">
              <thead>
                <tr className="border-b border-gray-300 dark:border-gray-700">
                  <th className="text-left py-2 pr-4">#</th>
                  <th className="text-left py-2 pr-4">Part ID</th>
                  <th className="text-left py-2 pr-4">Vendor</th>
                  <th className="text-left py-2 pr-4">Package</th>
                </tr>
              </thead>
              <tbody>
                {kbEntries.map((entry, idx) => (
                  <tr
                    key={entry.part_id ?? idx}
                    className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/70 transition-colors"
                  >
                    <td className="py-1.5 pr-4">{idx + 1}</td>
                    <td className="py-1.5 pr-4 font-mono text-xs">
                      {entry.part_id ?? "-"}
                    </td>
                    <td className="py-1.5 pr-4">
                      {entry.vendor ?? entry.manufacturer ?? "-"}
                    </td>
                    <td className="py-1.5 pr-4">
                      {entry.package ?? "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}

export default AdminDashboard;
