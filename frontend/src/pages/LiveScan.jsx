import { useState, useRef, useCallback, useEffect } from 'react';
import { Camera, CameraOff, ScanLine, Loader2, Brain } from 'lucide-react';
import { scanFrame, getParts } from '../utils/api';
import { useBackendStatus } from '../hooks/useBackendStatus';
import VerdictCard from '../components/VerdictCard';
import PipelineBanner from '../components/PipelineBanner';

export default function LiveScan() {
  const { status } = useBackendStatus();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [streaming, setStreaming] = useState(false);
  const [partId, setPartId] = useState('');
  const [useAi, setUseAi] = useState(false);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const streamRef = useRef(null);

  useEffect(() => {
    getParts().then((r) => setParts(r.data.parts || [])).catch(() => {});
    return () => stopCamera();
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment', width: 1280, height: 720 } });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setStreaming(true);
      setError('');
    } catch (err) {
      setError('Camera access denied. Please allow camera permissions.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setStreaming(false);
  };

  const captureAndScan = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current) return;
    setLoading(true);
    setError('');
    setResult(null);

    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    const base64 = canvas.toDataURL('image/jpeg', 0.9).split(',')[1];

    try {
      const { data } = await scanFrame(base64, partId || null, 'aho_corasick', useAi);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Scan failed.');
    } finally {
      setLoading(false);
    }
  }, [partId, useAi]);

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Live Camera Scan</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Point your camera at an IC chip and capture for instant verification</p>
      </div>

      <PipelineBanner mode="live" />

      <div className="rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-700 bg-black relative">
        <video ref={videoRef} className={`w-full aspect-video object-cover ${streaming ? '' : 'hidden'}`} playsInline muted />
        <canvas ref={canvasRef} className="hidden" />
        {!streaming && (
          <div className="w-full aspect-video flex flex-col items-center justify-center bg-gray-100 dark:bg-gray-800">
            <CameraOff className="w-16 h-16 text-gray-400 mb-4" />
            <p className="text-gray-500 dark:text-gray-400">Camera is off</p>
          </div>
        )}
        {streaming && (
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 border-2 border-primary-400/60 rounded-xl" />
          </div>
        )}
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Part ID (optional)</label>
          <select value={partId} onChange={(e) => setPartId(e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500">
            <option value="">Auto-detect</option>
            {parts.map((p) => <option key={p} value={p}>{p.toUpperCase()}</option>)}
          </select>
        </div>
        <div className="flex items-end">
          <label className="flex items-center gap-2 cursor-pointer px-3 py-2.5">
            <input type="checkbox" checked={useAi} onChange={(e) => setUseAi(e.target.checked)} className="w-4 h-4 rounded border-gray-300 text-primary-500" />
            <Brain className="w-4 h-4 text-accent-500" />
            <span className="text-sm text-gray-700 dark:text-gray-300">AI Analysis</span>
          </label>
        </div>
        <div className="flex items-end gap-2">
          {!streaming ? (
            <button onClick={startCamera} className="flex-1 py-2.5 rounded-lg bg-green-500 hover:bg-green-600 text-white font-medium flex items-center justify-center gap-2 transition-colors">
              <Camera className="w-4 h-4" /> Start Camera
            </button>
          ) : (
            <button onClick={stopCamera} className="flex-1 py-2.5 rounded-lg bg-red-500 hover:bg-red-600 text-white font-medium flex items-center justify-center gap-2 transition-colors">
              <CameraOff className="w-4 h-4" /> Stop
            </button>
          )}
        </div>
      </div>

      <button onClick={captureAndScan} disabled={!streaming || loading || status === 'offline'}
        className="w-full py-3 rounded-xl font-semibold text-white bg-primary-500 hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-lg shadow-primary-500/20">
        {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> Scanning...</> : <><ScanLine className="w-5 h-5" /> Capture & Verify</>}
      </button>

      {error && <div className="p-4 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-red-700 dark:text-red-400 text-sm">{error}</div>}
      {result && <VerdictCard result={result} />}
    </div>
  );
}
