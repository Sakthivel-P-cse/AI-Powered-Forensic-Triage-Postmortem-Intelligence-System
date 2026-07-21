const KEY = 'forensic_auth';

const USE_MOCKS = (import.meta.env.VITE_USE_MOCKS ?? 'true') === 'true';
const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const DEMO_USERS = [
  { email: 'investigator@forensic.local', password: 'demo', role: 'INVESTIGATOR', name: 'D. Iyer' },
  { email: 'analyst@forensic.local', password: 'demo', role: 'ANALYST', name: 'M. Krishnan' },
  { email: 'admin@forensic.local', password: 'demo', role: 'ADMIN', name: 'System Admin' },
];

function persist(session) {
  localStorage.setItem(KEY, JSON.stringify(session));
  return session;
}

async function loginLive(email, password) {
  const body = new URLSearchParams();
  body.set('username', email);
  body.set('password', password);
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text ? `Login failed: ${text}` : 'Invalid credentials');
  }
  const data = await res.json();
  return persist({
    token: data.access_token,
    user: { email, role: data.role, name: data.name },
    issuedAt: new Date().toISOString(),
  });
}

function loginMock(email, password) {
  const u = DEMO_USERS.find((x) => x.email === email && x.password === password);
  if (!u) throw new Error('Invalid credentials');
  return persist({
    token: `mock.jwt.${btoa(email)}.${Date.now()}`,
    user: { email: u.email, role: u.role, name: u.name },
    issuedAt: new Date().toISOString(),
  });
}

export async function login(email, password) {
  return USE_MOCKS ? loginMock(email, password) : loginLive(email, password);
}

export function logout() {
  localStorage.removeItem(KEY);
}

export function getSession() {
  try {
    const s = localStorage.getItem(KEY);
    return s ? JSON.parse(s) : null;
  } catch {
    return null;
  }
}

export function currentUser() {
  return getSession()?.user || null;
}

export function hasRole(...roles) {
  const u = currentUser();
  return !!u && roles.includes(u.role);
}
