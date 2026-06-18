import { WifiOff, RefreshCw, AlertTriangle } from 'lucide-react';
import { useBackendStatus } from '../hooks/useBackendStatus';

export default function BackendBanner() {
  const { status, retry } = useBackendStatus();

  if (status === 'online') return null;

  return (
    <div className={`px-4 py-3 text-sm flex items-center justify-center gap-3 ${
      status === 'offline'
        ? 'bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-400 border-b border-red-200 dark:border-red-500/20'
        : status === 'degraded'
        ? 'bg-yellow-50 dark:bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-b border-yellow-200 dark:border-yellow-500/20'
        : 'bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 border-b border-blue-200 dark:border-blue-500/20'
    }`}>
      {status === 'offline' ? (
        <>
          <WifiOff className="w-4 h-4 shrink-0" />
          <span>
            <strong>Backend unreachable.</strong> Start your backend server with{' '}
            <code className="px-1.5 py-0.5 rounded bg-red-100 dark:bg-red-500/20 font-mono text-xs">
              uvicorn app.main:app --reload
            </code>{' '}
            or check your deployment.
          </span>
        </>
      ) : status === 'degraded' ? (
        <>
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span><strong>Backend degraded.</strong> Some services may be unavailable.</span>
        </>
      ) : (
        <span>Checking backend status...</span>
      )}
      <button
        onClick={retry}
        className="shrink-0 p-1.5 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
        aria-label="Retry connection"
      >
        <RefreshCw className="w-4 h-4" />
      </button>
    </div>
  );
}
