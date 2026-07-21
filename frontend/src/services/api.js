import { mockCases } from '../data/mockCases.js';
import { getSession } from './auth.js';

const USE_MOCKS = (import.meta.env.VITE_USE_MOCKS ?? 'true') === 'true';
const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function authHeaders() {
  const t = getSession()?.token;
  return t ? { Authorization: `Bearer ${t}` } : {};
}

async function http(path, opts = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...authHeaders(), ...(opts.headers || {}) },
    ...opts,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`API ${res.status}${text ? ` — ${text}` : ''}`);
  }
  return res.json();
}

async function multipart(path, formData) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { ...authHeaders() },
    body: formData,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`API ${res.status}${text ? ` — ${text}` : ''}`);
  }
  return res.json();
}

export const api = {
  listCases: async () => (USE_MOCKS ? mockCases : http('/api/cases')),
  getCase: async (id) =>
    USE_MOCKS ? mockCases.find((c) => c.id === id) : http(`/api/cases/${id}`),
  getAutopsy: async (id) => {
    const c = await api.getCase(id);
    return c?.autopsy;
  },
  getCCTV: async (id) => {
    const c = await api.getCase(id);
    return c?.cctv;
  },
  getCorrelation: async (id) => {
    const c = await api.getCase(id);
    return c?.correlation;
  },
  getRisk: async (id) => {
    const c = await api.getCase(id);
    return c?.risk;
  },
  getGPS: async (id) => {
    const c = await api.getCase(id);
    return c?.gps;
  },
  uploadEvidence: async ({ caseId, fileType = 'autopsy', file }) => {
    if (USE_MOCKS) {
      // Mock: simulate a successful upload locally so the UI flow works without backend.
      await new Promise((r) => setTimeout(r, 350));
      return {
        id: `mock-${Math.random().toString(36).slice(2, 10)}`,
        case_id: caseId,
        file_type: fileType,
        storage_url: `mock://cases/${caseId}/${file.name}`,
        bytes_uploaded: file.size,
        ocr_text_excerpt:
          fileType === 'autopsy'
            ? '[mock] OCR not run in mock mode — wire backend to see real autopsy analysis.'
            : null,
        autopsy_analysis: null,
        upload_by: 'mock',
        created_at: new Date().toISOString(),
      };
    }
    const fd = new FormData();
    fd.append('case_id', caseId);
    fd.append('file_type', fileType);
    fd.append('file', file);
    return multipart('/api/evidence/upload', fd);
  },
  getDisputes: async (caseId) => http(`/api/disputes/${caseId}`),
  raiseDispute: async (payload) => http('/api/disputes', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  getSignoff: async (caseId) => http(`/api/signoff/${caseId}`),
  signOff: async (caseId, disputedFindings = []) => http(`/api/signoff/${caseId}`, {
    method: 'POST',
    body: JSON.stringify({ disputed_findings: disputedFindings }),
  }),
};
