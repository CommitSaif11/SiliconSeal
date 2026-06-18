import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getKB, reloadKB, enrichKB, getAIStatus } from '../utils/api';
import { Database, RefreshCw, Plus, Loader2, Bot, Shield } from 'lucide-react';

export default function Admin() {
  const { isAdmin } = useAuth();
  const navigate = useNavigate();
  const [kb, setKb] = useState([]);
  const [aiStatus, setAiStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reloading, setReloading] = useState(false);
  const [enrichPart, setEnrichPart] = useState('');
  const [enriching, setEnriching] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    if (!isAdmin) { navigate('/login'); return; }
    fetchData();
  }, [isAdmin]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [kbRes, aiRes] = await Promise.all([getKB(), getAIStatus()]);
      setKb(kbRes.data.entries || []);
      setAiStatus(aiRes.data);
    } catch (err) {
      setMsg('Failed to load data: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleReload = async () => {
    setReloading(true);
    try {
      const { data } = await reloadKB();
      setMsg(`KB reloaded: ${data.count} entries`);
      fetchData();
    } catch (err) {
      setMsg('Reload failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setReloading(false);
    }
  };

  const handleEnrich = async () => {
    if (!enrichPart.trim()) return;
    setEnriching(true);
    try {
      const { data } = await enrichKB(enrichPart.trim());
      setMsg(`${data.operation === 'update' ? 'Updated' : 'Added'} ${data.saved_part_id} (${data.kb_count} total)`);
      setEnrichPart('');
      fetchData();
    } catch (err) {
      setMsg('Enrich failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setEnriching(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Shield className="w-7 h-7 text-primary-500" /> Admin Dashboard
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Manage knowledge base and system configuration</p>
        </div>
      </div>

      {msg && (
        <div className="p-3 rounded-lg bg-primary-50 dark:bg-primary-500/10 border border-primary-200 dark:border-primary-500/20 text-primary-700 dark:text-primary-400 text-sm flex items-center justify-between">
          {msg}
          <button onClick={() => setMsg('')} className="text-xs hover:underline ml-4">Dismiss</button>
        </div>
      )}

      {/* Stats */}
      <div className="grid sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
          <Database className="w-6 h-6 text-primary-500 mb-2" />
          <div className="text-3xl font-bold text-gray-900 dark:text-white">{kb.length}</div>
          <div className="text-sm text-gray-500">KB Entries</div>
        </div>
        <div className="p-5 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
          <Bot className="w-6 h-6 text-accent-500 mb-2" />
          <div className="text-3xl font-bold text-gray-900 dark:text-white">{aiStatus?.ai_enabled ? 'Active' : 'Off'}</div>
          <div className="text-sm text-gray-500">AI Agent ({aiStatus?.model || 'N/A'})</div>
        </div>
        <div className="p-5 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
          <div className="text-3xl font-bold text-gray-900 dark:text-white">{new Set(kb.map((e) => e.oem)).size}</div>
          <div className="text-sm text-gray-500 mt-2">Unique OEMs</div>
        </div>
      </div>

      {/* Actions */}
      <div className="grid sm:grid-cols-2 gap-4">
        <div className="p-5 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 space-y-3">
          <h3 className="font-semibold text-gray-900 dark:text-white">Reload Knowledge Base</h3>
          <p className="text-sm text-gray-500">Rebuild the in-memory KB index from disk</p>
          <button onClick={handleReload} disabled={reloading}
            className="px-4 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium disabled:opacity-50 flex items-center gap-2 transition-colors">
            {reloading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
            {reloading ? 'Reloading...' : 'Reload KB'}
          </button>
        </div>

        <div className="p-5 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 space-y-3">
          <h3 className="font-semibold text-gray-900 dark:text-white">Enrich from Mouser</h3>
          <p className="text-sm text-gray-500">Fetch IC data from Mouser and add to KB</p>
          <div className="flex gap-2">
            <input
              value={enrichPart}
              onChange={(e) => setEnrichPart(e.target.value)}
              placeholder="e.g. STM32F103C8T6"
              className="flex-1 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
            />
            <button onClick={handleEnrich} disabled={enriching || !enrichPart.trim()}
              className="px-4 py-2 rounded-lg bg-accent-500 hover:bg-accent-600 text-white text-sm font-medium disabled:opacity-50 flex items-center gap-2 transition-colors">
              {enriching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>

      {/* KB Table */}
      <div className="rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="px-5 py-3 bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-700">
          <h3 className="font-semibold text-gray-900 dark:text-white">Knowledge Base Entries</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700 text-left">
                <th className="px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Part ID</th>
                <th className="px-5 py-3 text-xs font-semibold text-gray-500 uppercase">OEM</th>
                <th className="px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Package</th>
                <th className="px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Logo</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700/50">
              {kb.map((entry) => (
                <tr key={entry.part_id} className="hover:bg-gray-50 dark:hover:bg-white/5 transition-colors">
                  <td className="px-5 py-3 font-mono font-medium text-gray-900 dark:text-white">{entry.part_id}</td>
                  <td className="px-5 py-3 text-gray-600 dark:text-gray-300">{entry.oem}</td>
                  <td className="px-5 py-3 text-gray-500 dark:text-gray-400">{entry.package}</td>
                  <td className="px-5 py-3">
                    <span className="px-2 py-0.5 rounded bg-primary-100 dark:bg-primary-500/10 text-primary-700 dark:text-primary-400 text-xs font-medium">
                      {entry.logo_hint}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
