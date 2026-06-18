import { useState, useEffect, useCallback } from 'react';
import { checkHealth } from '../utils/api';

export function useBackendStatus(intervalMs = 30000) {
  const [status, setStatus] = useState('checking');
  const [info, setInfo] = useState(null);

  const check = useCallback(async () => {
    try {
      const { data } = await checkHealth();
      setStatus(data.status === 'healthy' ? 'online' : 'degraded');
      setInfo(data);
    } catch {
      setStatus('offline');
      setInfo(null);
    }
  }, []);

  useEffect(() => {
    check();
    const id = setInterval(check, intervalMs);
    return () => clearInterval(id);
  }, [check, intervalMs]);

  return { status, info, retry: check };
}
