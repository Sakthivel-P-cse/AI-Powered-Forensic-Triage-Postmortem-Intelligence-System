import { NavLink, Outlet, useLocation, useParams, useNavigate } from 'react-router-dom';
import { currentUser, logout } from '../services/auth.js';

function CrumbNav() {
  const { id } = useParams();
  const loc = useLocation();

  if (!id) return null;
  const tabs = [
    { to: `/cases/${id}`, label: 'Overview', exact: true },
    { to: `/cases/${id}/autopsy`, label: 'Autopsy' },
    { to: `/cases/${id}/cctv`, label: 'CCTV' },
    { to: `/cases/${id}/correlation`, label: 'Correlation' },
    { to: `/cases/${id}/map`, label: 'Map' },
    { to: `/cases/${id}/risk`, label: 'Risk' },
    { to: `/cases/${id}/report`, label: 'Report' },
  ];
  return (
    <div className="border-b border-forensic-border bg-forensic-surface/60 backdrop-blur">
      <div className="max-w-7xl mx-auto px-6 flex items-center gap-2 overflow-x-auto">
        <span className="label mr-3">Case</span>
        <span className="mono text-forensic-accent">{id}</span>
        <div className="flex-1" />
        <nav className="flex gap-1">
          {tabs.map((t) => {
            const active =
              t.exact ? loc.pathname === t.to : loc.pathname.startsWith(t.to);
            return (
              <NavLink
                key={t.to}
                to={t.to}
                end={t.exact}
                className={`px-3 py-2.5 text-sm border-b-2 -mb-px ${
                  active
                    ? 'border-forensic-accent text-forensic-accent'
                    : 'border-transparent text-forensic-muted hover:text-forensic-text'
                }`}
              >
                {t.label}
              </NavLink>
            );
          })}
        </nav>
      </div>
    </div>
  );
}

export default function Layout() {
  const user = currentUser();
  const nav = useNavigate();
  return (
    <div className="min-h-full flex flex-col">
      {/* Top bar */}
      <header className="border-b border-forensic-border bg-forensic-bg/80 backdrop-blur sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center gap-4">
          <NavLink to="/cases" className="flex items-center gap-2.5">
            <svg width="22" height="22" viewBox="0 0 64 64">
              <path d="M14 44 L32 14 L50 44 Z" fill="none" stroke="#00C8FF" strokeWidth="3" />
              <circle cx="32" cy="36" r="3" fill="#00C8FF" />
            </svg>
            <div className="leading-tight">
              <div className="text-sm font-semibold tracking-wide">Forensic Triage</div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-forensic-muted">
                Postmortem Intelligence
              </div>
            </div>
          </NavLink>
          <div className="flex-1" />
          <div className="hidden md:flex items-center gap-2">
            <span className="chip border-forensic-border text-forensic-muted">
              <span className="w-1.5 h-1.5 rounded-full bg-forensic-ok" /> system online
            </span>
            <span className="chip border-forensic-accent/40 text-forensic-accent">
              FIPL v0.1
            </span>
          </div>
          {user && (
            <div className="flex items-center gap-3 pl-3 border-l border-forensic-border">
              <div className="text-right leading-tight">
                <div className="text-sm">{user.name}</div>
                <div className="text-[10px] uppercase tracking-[0.2em] text-forensic-muted mono">
                  {user.role}
                </div>
              </div>
              <button
                onClick={() => {
                  logout();
                  nav('/login', { replace: true });
                }}
                className="btn-ghost text-xs"
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      </header>
      <CrumbNav />
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-6">
        <Outlet />
      </main>
      <footer className="border-t border-forensic-border py-4 text-center text-[11px] text-forensic-muted mono">
        AI-assisted analysis · Outputs are investigative support only · Human sign-off required for export
      </footer>
    </div>
  );
}
