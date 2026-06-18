import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export const checkHealth = () => api.get('/health');

export const getParts = () => api.get('/parts');

export const scanImage = (file, partId, algorithm, useAi) => {
  const form = new FormData();
  form.append('file', file);
  if (partId) form.append('part_id', partId);
  form.append('algorithm', algorithm || 'aho_corasick');
  form.append('use_ai', useAi ? 'true' : 'false');
  return api.post('/scan', form);
};

export const scanBatch = (files, partId, algorithm) => {
  const form = new FormData();
  files.forEach((f) => form.append('files', f));
  if (partId) form.append('part_id', partId);
  form.append('algorithm', algorithm || 'regex');
  return api.post('/scan/batch', form);
};

export const scanFrame = (base64, partId, algorithm, useAi) => {
  const form = new FormData();
  form.append('frame', base64);
  if (partId) form.append('part_id', partId);
  form.append('algorithm', algorithm || 'aho_corasick');
  form.append('use_ai', useAi ? 'true' : 'false');
  return api.post('/scan/frame', form);
};

export const login = (username, password) => {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  return api.post('/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
};

export const getKB = () => api.get('/kb');
export const reloadKB = () => api.post('/admin/reload-kb');
export const getAIStatus = () => api.get('/ai/status');
export const enrichKB = (part) => api.post(`/admin/kb/enrich-and-save?part=${encodeURIComponent(part)}`);

export default api;
