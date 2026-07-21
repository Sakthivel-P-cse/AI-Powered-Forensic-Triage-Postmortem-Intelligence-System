import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { api } from '../services/api.js';
import TimelineViewer from '../components/TimelineViewer.jsx';
import AIOutputCard from '../components/AIOutputCard.jsx';
import EvidenceUpload from '../components/EvidenceUpload.jsx';

export default function CCTVTimeline() {
  const { id } = useParams();
  const [c, setC] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCase(id).then(setC).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-forensic-muted p-10 text-center animate-pulse">Loading data...</div>;
  const cctv = c?.cctv;

  if (!c || !cctv) {
    return (
      <div className="space-y-4">
        <div className="panel panel-pad text-forensic-muted text-sm">No CCTV data.</div>
        <EvidenceUpload caseId={id} defaultType="cctv_log" />
      </div>
    );
  }

  const tlEvents = cctv.sorted_events.map((e) => ({
    ts: e.timestamp,
    source: 'CCTV',
    label: `${e.camera_id} · ${e.event_type}`,
  }));

  return (
    <div className="space-y-6">
      <EvidenceUpload caseId={id} defaultType="cctv_log" />

      <TimelineViewer events={tlEvents} />

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Gaps */}
        <section className="panel">
          <div className="px-5 py-3 border-b border-forensic-border flex items-center gap-2">
            <span className="label">Coverage gaps</span>
            <span className="chip border-forensic-warn/40 text-forensic-warn ml-auto">
              {cctv.gaps.length} flagged
            </span>
          </div>
          <ul className="divide-y divide-forensic-border">
            {cctv.gaps.length === 0 && (
              <li className="px-5 py-6 text-forensic-muted text-sm">
                No gaps above threshold.
              </li>
            )}
            {cctv.gaps.map((g, i) => (
              <li key={i} className="px-5 py-3 text-sm">
                <div className="flex justify-between">
                  <span className="mono text-forensic-accent">
                    {new Date(g.start).toLocaleTimeString()} →{' '}
                    {new Date(g.end).toLocaleTimeString()}
                  </span>
                  <span className="mono text-forensic-warn">
                    {g.duration_min.toFixed(1)} min
                  </span>
                </div>
                <div className="text-forensic-muted mt-1">{g.flag_reason}</div>
              </li>
            ))}
          </ul>
        </section>

        {/* Anomalies */}
        <section className="panel">
          <div className="px-5 py-3 border-b border-forensic-border flex items-center gap-2">
            <span className="label">Behavioral anomalies</span>
          </div>
          <ul className="divide-y divide-forensic-border">
            {cctv.anomalies.map((a, i) => (
              <li key={i} className="px-5 py-3 text-sm flex items-start gap-3">
                <span
                  className={`chip ${
                    a.severity === 'HIGH'
                      ? 'border-forensic-danger/40 text-forensic-danger'
                      : a.severity === 'MEDIUM'
                      ? 'border-forensic-warn/40 text-forensic-warn'
                      : 'border-forensic-border text-forensic-muted'
                  }`}
                >
                  {a.severity}
                </span>
                <span>{a.description}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>

      {/* Raw events */}
      <section className="panel overflow-hidden">
        <div className="px-5 py-3 border-b border-forensic-border label">Sorted log events</div>
        <table className="w-full text-sm">
          <thead className="text-forensic-muted">
            <tr className="text-left">
              <th className="px-5 py-2 font-medium label">Timestamp</th>
              <th className="px-5 py-2 font-medium label">Camera</th>
              <th className="px-5 py-2 font-medium label">Location</th>
              <th className="px-5 py-2 font-medium label">Event</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-forensic-border">
            {cctv.sorted_events.map((e) => (
              <tr key={e.id} className="hover:bg-forensic-surface/50">
                <td className="px-5 py-2 mono text-forensic-accent">
                  {new Date(e.timestamp).toLocaleTimeString()}
                </td>
                <td className="px-5 py-2 mono">{e.camera_id}</td>
                <td className="px-5 py-2">{e.location}</td>
                <td className="px-5 py-2 text-forensic-muted">{e.event_type}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <AIOutputCard
        title="Movement narrative"
        reasoning={cctv.reasoning_chain}
        caseId={id}
        findingId="cctv_narrative"
      >
        <p className="leading-relaxed">{cctv.movement_summary}</p>
        {cctv.risk_flags.length > 0 && (
          <div className="mt-3">
            <div className="label mb-1.5">Risk flags</div>
            <ul className="text-sm">
              {cctv.risk_flags.map((f, i) => (
                <li key={i} className="text-forensic-warn">⚑ {f}</li>
              ))}
            </ul>
          </div>
        )}
      </AIOutputCard>
    </div>
  );
}
