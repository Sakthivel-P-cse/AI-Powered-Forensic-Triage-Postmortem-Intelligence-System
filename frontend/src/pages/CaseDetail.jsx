import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api.js';
import RiskGauge from '../components/RiskGauge.jsx';
import EvidenceCard from '../components/EvidenceCard.jsx';
import TimelineViewer from '../components/TimelineViewer.jsx';

export default function CaseDetail() {
  const { id } = useParams();
  const [c, setC] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCase(id).then(setC).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-forensic-muted p-10 text-center animate-pulse">Loading case details...</div>;
  if (!c) return <div className="text-forensic-muted p-10 text-center">Case not found.</div>;

  const cctvCount = c.cctv?.sorted_events?.length || 0;
  const gpsCount = c.gps?.length || 0;
  const cContrs = c.correlation?.contradictions?.length || 0;
  const impossible = c.correlation?.contradictions?.filter((x) => x.type === 'IMPOSSIBLE').length || 0;

  return (
    <div className="space-y-6">
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Risk */}
        <div className="panel panel-pad lg:col-span-1">
          <div className="label">Risk score</div>
          <div className="mt-3 flex justify-center">
            <RiskGauge score={c.risk.score} level={c.risk.level} />
          </div>
          <div className="mt-4 text-xs text-forensic-muted">
            Deterministic weighted scoring. Gemini provides the briefing — never the score.
          </div>
        </div>

        {/* Evidence summary */}
        <div className="lg:col-span-2 grid sm:grid-cols-2 gap-4">
          <EvidenceCard
            label="Autopsy"
            value={c.autopsy ? c.autopsy.cause_of_death.value : '—'}
            sub={
              c.autopsy
                ? `confidence ${(c.autopsy.overall_confidence * 100).toFixed(0)}%`
                : 'no report uploaded'
            }
          />
          <EvidenceCard
            label="CCTV log events"
            value={cctvCount.toString()}
            sub={`${c.cctv?.gaps?.length || 0} flagged gap${(c.cctv?.gaps?.length || 0) === 1 ? '' : 's'}`}
          />
          <EvidenceCard
            label="GPS pings"
            value={gpsCount.toString()}
            sub={`${gpsCount > 0 ? 'phone + vehicle' : 'no data'}`}
          />
          <EvidenceCard
            accent={impossible > 0}
            label="Contradictions"
            value={cContrs.toString()}
            sub={impossible > 0 ? `${impossible} IMPOSSIBLE` : 'none impossible'}
          />
        </div>
      </div>

      {/* Briefing */}
      <section className="panel">
        <div className="flex items-center gap-3 px-5 pt-4 pb-3 border-b border-forensic-border">
          <span className="chip border-forensic-accent/40 text-forensic-accent">AI-assisted briefing</span>
          <h3 className="text-sm font-semibold">Investigation summary</h3>
          <span className="ml-auto label">requires human review</span>
        </div>
        <div className="panel-pad">
          <p className="leading-relaxed">{c.risk.briefing}</p>
          <div className="grid md:grid-cols-2 gap-6 mt-5">
            <div>
              <div className="label mb-2">Recommended next steps</div>
              <ol className="space-y-1.5 text-sm">
                {c.risk.next_steps.map((s, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="mono text-forensic-accent text-xs pt-0.5">{i + 1}.</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ol>
            </div>
            <div>
              <div className="label mb-2">Caveats</div>
              <ul className="space-y-1.5 text-sm text-forensic-muted">
                {c.risk.caveats.map((s, i) => (
                  <li key={i}>· {s}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Timeline preview */}
      {c.correlation?.unified_timeline?.length > 0 && (
        <TimelineViewer
          events={c.correlation.unified_timeline.map((e) => ({
            ts: e.ts,
            source: e.source,
            label: e.label,
          }))}
        />
      )}

      {/* Quick links */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          ['Autopsy', `/cases/${id}/autopsy`],
          ['CCTV timeline', `/cases/${id}/cctv`],
          ['Contradiction matrix', `/cases/${id}/correlation`],
          ['Risk breakdown', `/cases/${id}/risk`],
        ].map(([label, to]) => (
          <Link key={to} to={to} className="panel panel-pad hover:border-forensic-accent/40 hover:shadow-glow transition">
            <div className="flex items-center justify-between">
              <span className="text-sm">{label}</span>
              <span className="text-forensic-accent">→</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
