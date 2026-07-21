import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { login, getSession } from '../services/auth.js';

const PRESETS = [
  { role: 'INVESTIGATOR', email: 'investigator@forensic.local' },
  { role: 'ANALYST', email: 'analyst@forensic.local' },
  { role: 'ADMIN', email: 'admin@forensic.local' },
];

export default function Login() {
  const nav = useNavigate();
  const loc = useLocation();
  const [email, setEmail] = useState('analyst@forensic.local');
  const [password, setPassword] = useState('demo');
  const [err, setErr] = useState('');

  if (getSession()) {
    nav('/cases', { replace: true });
  }

  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr('');
    setBusy(true);
    try {
      await login(email, password);
      const to = loc.state?.from?.pathname || '/cases';
      nav(to, { replace: true });
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen grid md:grid-cols-2">
      {/* Left brand panel */}
      <div className="relative hidden md:flex flex-col justify-between p-10 border-r border-forensic-border overflow-hidden">
        <div className="absolute inset-0 gridline opacity-30" />
        <div className="relative">
          <div className="flex items-center gap-3">
            <svg width="34" height="34" viewBox="0 0 64 64">
              <path d="M14 44 L32 14 L50 44 Z" fill="none" stroke="#00C8FF" strokeWidth="3" />
              <circle cx="32" cy="36" r="3" fill="#00C8FF" />
            </svg>
            <div>
              <div className="text-xl font-semibold tracking-wide">Forensic Triage</div>
              <div className="label">Postmortem Intelligence System</div>
            </div>
          </div>
          <p className="mt-10 text-2xl leading-snug max-w-md text-forensic-text/90">
            Cross-source contradiction detection,
            <span className="text-forensic-accent"> hybrid time-of-death estimation</span>,
            and analyst-gated reporting — all auditable.
          </p>
          <ul className="mt-8 space-y-2 text-sm text-forensic-muted">
            <li>· Deterministic engines compute. AI explains.</li>
            <li>· Every inference returns a reasoning chain.</li>
            <li>· No report exports without a Forensic Analyst sign-off.</li>
          </ul>
        </div>
        <div className="relative text-[11px] text-forensic-muted mono">
          v0.1 · FIPL prompt layer · Gemini-backed inference
        </div>
      </div>

      {/* Right form */}
      <div className="flex items-center justify-center p-6">
        <form onSubmit={submit} className="panel panel-pad w-full max-w-md space-y-5">
          <div>
            <h1 className="text-lg font-semibold">Authenticate</h1>
            <p className="text-sm text-forensic-muted mt-1">
              Use any preset · password{' '}
              <span className="mono text-forensic-text">demo</span>
            </p>
          </div>

          <div>
            <label className="label">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full bg-forensic-bg border border-forensic-border rounded-md px-3 py-2 mono text-sm"
              required
            />
          </div>

          <div>
            <label className="label">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full bg-forensic-bg border border-forensic-border rounded-md px-3 py-2 mono text-sm"
              required
            />
          </div>

          {err && (
            <div className="text-sm text-forensic-danger border border-forensic-danger/40 bg-forensic-danger/10 rounded-md px-3 py-2">
              {err}
            </div>
          )}

          <button
            className="btn-primary w-full justify-center"
            type="submit"
            disabled={busy}
          >
            {busy ? 'Signing in…' : 'Sign in'}
          </button>

          <div className="divider" />
          <div className="space-y-2">
            <div className="label">Quick switch</div>
            <div className="grid grid-cols-3 gap-2">
              {PRESETS.map((p) => (
                <button
                  type="button"
                  key={p.role}
                  className="btn-ghost text-xs justify-center"
                  onClick={() => {
                    setEmail(p.email);
                    setPassword('demo');
                  }}
                >
                  {p.role}
                </button>
              ))}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
