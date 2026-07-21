import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../services/api.js';
import SignOffGate from '../components/SignOffGate.jsx';
import RiskBadge from '../components/RiskBadge.jsx';

function Section({ title, children }) {
  return (
    <section className="panel">
      <div className="px-5 py-3 border-b border-forensic-border label">{title}</div>
      <div className="px-5 py-4 text-sm leading-relaxed">{children}</div>
    </section>
  );
}

export default function ReportView() {
  const { id } = useParams();
  const [c, setC] = useState(null);
  const [signoff, setSignoff] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getCase(id).catch(() => null),
      api.getSignoff(id).catch(() => null)
    ]).then(([caseData, signoffData]) => {
      setC(caseData);
      setSignoff(signoffData);
    }).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-forensic-muted p-10 text-center animate-pulse">Loading report...</div>;
  if (!c) return null;

  const a = c.autopsy;
  const cor = c.correlation;

  return (
    <div className="space-y-6">
      <SignOffGate caseId={id} />

      {/* Cover */}
      <section className="panel panel-pad">
        <div className="flex items-center gap-3">
          <span className="chip border-forensic-accent/40 text-forensic-accent">DRAFT REPORT</span>
          <span className="mono text-forensic-muted">{c.id}</span>
          <RiskBadge level={c.risk.level} score={c.risk.score} />
          <div className="ml-auto text-xs mono text-forensic-muted">
            generated {new Date().toLocaleString()}
          </div>
        </div>
        <h1 className="text-2xl font-semibold mt-3">{c.title}</h1>
        <div className="text-sm text-forensic-muted mt-1">
          Case opened {new Date(c.created_at).toLocaleString()} · status{' '}
          <span className="mono text-forensic-text">{c.status}</span>
        </div>
      </section>

      <Section title="Executive summary">
        <p>{c.risk.briefing}</p>
      </Section>

      {a && (
        <Section title="Autopsy findings">
          <ul className="space-y-1.5">
            <li>
              <span className="label">Cause:</span> {a.cause_of_death.value}
            </li>
            <li>
              <span className="label">Manner:</span> {a.manner_of_death.value}
            </li>
            <li>
              <span className="label">TOD window:</span>{' '}
              <span className="mono">
                {a.tod_estimate.corrected_window_hours[0]}–
                {a.tod_estimate.corrected_window_hours[1]}h
              </span>{' '}
              · confidence {a.tod_estimate.confidence}
            </li>
          </ul>
          <p className="mt-3">{a.summary}</p>
        </Section>
      )}

      {cor && cor.contradictions.length > 0 && (
        <Section title="Cross-source contradictions">
          <ol className="space-y-3 list-decimal list-inside">
            {cor.contradictions.map((x) => (
              <li key={x.id}>
                <span className="mono text-forensic-text">{x.type}</span>{' '}
                — {x.distance_km.toFixed(2)} km in {x.time_delta_min.toFixed(1)} min ·{' '}
                priority{' '}
                <span className="mono text-forensic-warn">{x.investigative_priority}</span>
                <div className="text-forensic-muted text-sm mt-1">{x.explanation}</div>
              </li>
            ))}
          </ol>
        </Section>
      )}

      <Section title="Recommended next steps">
        <ol className="list-decimal list-inside space-y-1">
          {c.risk.next_steps.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ol>
      </Section>

      <Section title="Caveats and limitations">
        <ul className="space-y-1">
          {c.risk.caveats.map((s, i) => (
            <li key={i}>· {s}</li>
          ))}
          <li>
            · This document is AI-assisted investigative support and is not a forensic
            conclusion. Final determinations require certified examiner review.
          </li>
        </ul>
      </Section>

      <div className="text-[11px] text-forensic-muted mono text-center pt-4">
        {signoff
          ? `Signed by ${signoff.analyst} at ${new Date(signoff.at).toLocaleString()} · audit-logged`
          : 'Unsigned — export disabled'}
      </div>
    </div>
  );
}
