import { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, ScanLine, Loader2, ImageIcon, X, Brain, FlaskConical } from 'lucide-react';
import { scanImage, getParts } from '../utils/api';
import { useBackendStatus } from '../hooks/useBackendStatus';
import VerdictCard from '../components/VerdictCard';
import { generateDemoFile, getDemoPreviewUrl, DEMO_NAMES, DEMO_COUNT } from '../utils/demoImages';
import PipelineBanner from '../components/PipelineBanner';

export default function Scan() {
  const { status } = useBackendStatus();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [partId, setPartId] = useState('');
  const [algorithm, setAlgorithm] = useState('aho_corasick');
  const [useAi, setUseAi] = useState(true);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    getParts().then((r) => setParts(r.data.parts || [])).catch(() => {});
  }, []);

  const onDrop = useCallback((accepted) => {
    if (accepted.length > 0) {
      const f = accepted[0];
      setFile(f);
      setPreview(URL.createObjectURL(f));
      setResult(null);
      setError('');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.bmp', '.webp'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  const handleScan = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const { data } = await scanImage(file, partId || null, algorithm, useAi);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Scan failed. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError('');
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Single IC Scan</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Upload an IC image for automated verification</p>
      </div>

      <PipelineBanner mode="scan" />

      {/* Upload Zone */}
      {!file ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/5'
              : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <p className="text-lg font-medium text-gray-700 dark:text-gray-300">
            {isDragActive ? 'Drop your IC image here' : 'Drag & drop an IC image, or click to browse'}
          </p>
          <p className="text-sm text-gray-400 mt-2">PNG, JPG, BMP, WebP — Max 10 MB</p>
        </div>
      ) : (
        <div className="relative rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <button
            onClick={clearFile}
            className="absolute top-3 right-3 z-10 p-1.5 rounded-lg bg-black/50 text-white hover:bg-black/70 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
          <div className="flex items-center justify-center bg-gray-50 dark:bg-gray-800/50 p-4">
            <img src={preview} alt="IC preview" className="max-h-64 rounded-lg object-contain" />
          </div>
          <div className="px-4 py-3 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 flex items-center gap-2">
            <ImageIcon className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600 dark:text-gray-300 truncate">{file.name}</span>
            <span className="text-xs text-gray-400 ml-auto">{(file.size / 1024).toFixed(0)} KB</span>
          </div>
        </div>
      )}

      {/* Demo Images */}
      {!file && (
        <div className="rounded-xl border border-dashed border-accent-400/40 bg-accent-500/5 p-4">
          <div className="flex items-center gap-2 mb-3">
            <FlaskConical className="w-4 h-4 text-accent-500" />
            <span className="text-sm font-semibold text-accent-600 dark:text-accent-400">Try Demo IC Images</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {DEMO_NAMES.map((name, i) => (
              <button
                key={name}
                onClick={async () => {
                  const f = await generateDemoFile(i);
                  setFile(f);
                  setPreview(getDemoPreviewUrl(i));
                  setResult(null);
                  setError('');
                }}
                className="px-3 py-1.5 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs font-mono font-medium text-gray-700 dark:text-gray-300 hover:border-accent-400 hover:text-accent-600 dark:hover:text-accent-400 transition-all"
              >
                {name.replace('.png', '')}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="grid sm:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Part ID (optional)</label>
          <select
            value={partId}
            onChange={(e) => setPartId(e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">Auto-detect</option>
            {parts.map((p) => (
              <option key={p} value={p}>{p.toUpperCase()}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Algorithm</label>
          <select
            value={algorithm}
            onChange={(e) => setAlgorithm(e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="aho_corasick">Aho-Corasick (Auto-detect)</option>
            <option value="regex">Regex (Known IC)</option>
          </select>
        </div>

        <div className="flex items-end">
          <label className="flex items-center gap-2 cursor-pointer px-3 py-2.5">
            <input
              type="checkbox"
              checked={useAi}
              onChange={(e) => setUseAi(e.target.checked)}
              className="w-4 h-4 rounded border-gray-300 text-primary-500 focus:ring-primary-500"
            />
            <Brain className="w-4 h-4 text-accent-500" />
            <span className="text-sm text-gray-700 dark:text-gray-300">AI Analysis</span>
          </label>
        </div>
      </div>

      {/* Scan Button */}
      <button
        onClick={handleScan}
        disabled={!file || loading || status === 'offline'}
        className="w-full py-3 px-6 rounded-xl font-semibold text-white bg-primary-500 hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-lg shadow-primary-500/20"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            {useAi ? 'Scanning & Analyzing...' : 'Scanning...'}
          </>
        ) : (
          <>
            <ScanLine className="w-5 h-5" />
            Verify IC
          </>
        )}
      </button>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-red-700 dark:text-red-400 text-sm">
          {error}
        </div>
      )}

      {result && <VerdictCard result={result} />}
    </div>
  );
}
