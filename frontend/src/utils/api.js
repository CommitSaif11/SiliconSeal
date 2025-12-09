import axios from "axios";

export const API_BASE = "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE,
});

export const apiGet = (url) => api.get(url);
export const apiPost = (url, data, config = {}) =>
  api.post(url, data, config);
