import { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Loader2, Trash2, FlaskConical } from 'lucide-react';
import { scanBatch, getParts } from '../utils/api';
import { useBackendStatus } from '../hooks/useBackendStatus';
import VerdictCard from '../components/VerdictCard';
import { generateAllDemoFiles } from '../utils/demoImages';
import PipelineBanner from '../components/PipelineBanner';

export default function BatchScan() {
  const { status } = useBackendStatus();
  const [files, setFiles] = useState([]);
  const [partId, setPartId] = useState('');
  const [algorithm, setAlgorithm] = useState('regex');
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    getParts().then((r) => setParts(r.data.parts || [])).catch(() => {});
  }, []);

  const onDrop = useCallback((accepted) => {
    setFiles((prev) => [...prev, ...accepted].slice(0, 20));
    setResults(null);
    setError('');
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.bmp', '.webp'] },
    maxSize: 10 * 1024 * 1024,
  });

  const handleScan = async () => {
    if (files.length === 0) return;
    setLoading(true);
    setError('');
    setResults(null);
    try {
      const { data } = await scanBatch(files, partId || null, algorithm);
      setResults(data.results || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Batch scan failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Batch Scan</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Upload multiple IC images for bulk verification (max 20)</p>
      </div>

      <PipelineBanner mode="batch" />

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
          isDragActive ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/5' : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-10 h-10 mx-auto text-gray-400 mb-3" />
        <p className="text-gray-700 dark:text-gray-300 font-medium">Drop IC images here, or click to browse</p>
        <p className="text-sm text-gray-400 mt-1">{files.length}/20 files selected</p>
      </div>

      {files.length === 0 && (
        <button
          onClick={async () => {
            const demos = await generateAllDemoFiles();
            setFiles(demos);
            setResults(null);
            setError('');
          }}
          className="w-full py-3 rounded-xl border border-dashed border-accent-400/40 bg-accent-500/5 text-accent-600 dark:text-accent-400 font-medium flex items-center justify-center gap-2 hover:bg-accent-500/10 transition-colors"
        >
          <FlaskConical className="w-4 h-4" /> Load 5 Demo IC Images
        </button>
      )}

      {files.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Selected Files</h3>
            <button onClick={() => { setFiles([]); setResults(null); }} className="text-xs text-red-500 hover:text-red-600 flex items-center gap-1">
              <Trash2 className="w-3 h-3" /> Clear all
            </button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {files.map((f, i) => (
              <div key={i} className="relative group">
                <img src={URL.createObjectURL(f)} alt={f.name} className="w-full h-24 object-cover rounded-lg border border-gray-200 dark:border-gray-700" />
                <button
                  onClick={() => setFiles((prev) => prev.filter((_, j) => j !== i))}
                  className="absolute top-1 right-1 p-1 rounded bg-black/50 text-white opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
                <p className="text-xs text-gray-500 truncate mt-1">{f.name}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Part ID</label>
          <select value={partId} onChange={(e) => setPartId(e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500">
            <option value="">Auto-detect</option>
            {parts.map((p) => <option key={p} value={p}>{p.toUpperCase()}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Algorithm</label>
          <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500">
            <option value="regex">Regex (Known IC)</option>
            <option value="aho_corasick">Aho-Corasick (Auto-detect)</option>
          </select>
        </div>
      </div>

      <button onClick={handleScan} disabled={files.length === 0 || loading || status === 'offline'}
        className="w-full py-3 rounded-xl font-semibold text-white bg-primary-500 hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2">
        {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> Processing {files.length} images...</> : `Scan ${files.length} Images`}
      </button>

      {error && <div className="p-4 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-red-700 dark:text-red-400 text-sm">{error}</div>}

      {results && (
        <div className="space-y-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Results ({results.length})</h2>
          <div className="grid gap-6">
            {results.map((r, i) => (
              <div key={i}>
                {r.filename && <p className="text-sm font-medium text-gray-500 mb-2">{r.filename}</p>}
                {r.status === 'error' ? (
                  <div className="p-4 rounded-xl bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400 text-sm">Error: {r.error}</div>
                ) : (
                  <VerdictCard result={r} />
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
