import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: API_URL });

export const Logs = {
  seed: (count) => api.post("/logs/seed", { count }),
  create: (payload) => api.post("/logs", payload).then((r) => r.data),
  list: (params) => api.get("/logs", { params }).then((r) => r.data),
  stats: () => api.get("/logs/stats/summary").then((r) => r.data),
};

export const Sampling = {
  run: (mode, n) => api.post("/sampling/run", { mode, n }).then((r) => r.data),
};

export const Clusters = {
  run: (payload) => api.post("/clusters/run", payload).then((r) => r.data),
  list: () => api.get("/clusters").then((r) => r.data),
};

export const Labeling = {
  candidates: (limit) => api.get("/labeling/candidates", { params: { limit } }).then((r) => r.data),
  generate: (log_ids) => api.post("/labeling/generate", { log_ids }).then((r) => r.data),
};

export const Review = {
  queue: (limit) => api.get("/review/queue", { params: { limit } }).then((r) => r.data),
  context: (caseId) => api.get(`/review/queue/${caseId}/context`).then((r) => r.data),
  act: (caseId, payload) => api.post(`/review/queue/${caseId}/action`, payload).then((r) => r.data),
};

export const Exports = {
  health: () => api.get("/export/health").then((r) => r.data),
  jsonlUrl: () => `${API_URL}/export/jsonl`,
};

export default api;
