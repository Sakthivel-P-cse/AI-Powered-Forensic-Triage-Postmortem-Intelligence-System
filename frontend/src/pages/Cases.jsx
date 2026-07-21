import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api.js';
import RiskBadge from '../components/RiskBadge.jsx';

export default function Cases() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState('');
  const [level, setLevel] = useState('ALL');

  useEffect(() => {
    api.listCases()
      .then(setCases)
      .catch(e => console.error("Failed to fetch cases:", e))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-forensic-muted text-center animate-pulse">Loading cases...</div>;

  const filtered = cases.filter(
    (c) =>
      (level === 'ALL' || c.risk.level === level) &&
      (c.id.toLowerCase().includes(q.toLowerCase()) ||
        c.title.toLowerCase().includes(q.toLowerCase()))
  );

  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-semibold">Active cases</h1>
          <p className="text-sm text-forensic-muted mt-1">
            {filtered.length} of {cases.length} shown · sorted by triage priority
          </p>
        </div>
        <div className="flex items-center gap-2">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search case id or title…"
            className="bg-forensic-bg border border-forensic-border rounded-md px-3 py-2 text-sm w-72 mono placeholder:text-forensic-muted/70"
          />
          <select
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className="bg-forensic-bg border border-forensic-border rounded-md px-2 py-2 text-sm"
          >
            <option value="ALL">All levels</option>
            <option>LOW</option>
            <option>MEDIUM</option>
            <option>HIGH</option>
            <option>CRITICAL</option>
          </select>
        </div>
      </div>

      <div className="panel overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-forensic-surface/60 text-forensic-muted">
            <tr className="text-left">
              <th className="px-5 py-3 font-medium label">Case ID</th>
              <th className="px-5 py-3 font-medium label">Title</th>
              <th className="px-5 py-3 font-medium label">Status</th>
              <th className="px-5 py-3 font-medium label">Risk</th>
              <th className="px-5 py-3 font-medium label">Top contradiction</th>
              <th className="px-5 py-3 font-medium label">Created</th>
              <th className="px-5 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-forensic-border">
            {filtered.map((c) => {
              const top = c.correlation?.contradictions?.[0];
              return (
                <tr key={c.id} className="hover:bg-forensic-surface/50">
                  <td className="px-5 py-3 mono text-forensic-accent">{c.id}</td>
                  <td className="px-5 py-3">{c.title}</td>
                  <td className="px-5 py-3">
                    <span className="chip border-forensic-border text-forensic-muted">
                      {c.status}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <RiskBadge level={c.risk.level} score={c.risk.score} />
                  </td>
                  <td className="px-5 py-3 text-forensic-muted">
                    {top ? (
                      <span>
                        <span className="mono text-forensic-text">{top.type}</span>{' '}
                        — {top.distance_km.toFixed(1)} km in {top.time_delta_min.toFixed(1)} min
                      </span>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td className="px-5 py-3 mono text-forensic-muted">
                    {new Date(c.created_at).toLocaleString(undefined, {
                      day: '2-digit',
                      month: 'short',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </td>
                  <td className="px-5 py-3 text-right">
                    <Link to={`/cases/${c.id}`} className="btn-primary text-xs">
                      Open
                    </Link>
                  </td>
                </tr>
              );
            })}
            {filtered.length === 0 && (
              <tr>
                <td colSpan="7" className="px-5 py-10 text-center text-forensic-muted">
                  No cases match the current filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
