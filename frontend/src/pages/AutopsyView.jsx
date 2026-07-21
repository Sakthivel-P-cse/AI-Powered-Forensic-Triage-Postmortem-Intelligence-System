import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { api } from '../services/api.js';
import AIOutputCard from '../components/AIOutputCard.jsx';
import EvidenceUpload from '../components/EvidenceUpload.jsx';

function Field({ label, children, mono = false }) {
  return (
    <div>
      <div className="label">{label}</div>
      <div className={`mt-1 text-sm ${mono ? 'mono' : ''}`}>{children}</div>
    </div>
  );
}

export default function AutopsyView() {
  const { id } = useParams();
  const [c, setC] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCase(id).then(setC).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-forensic-muted p-10 text-center animate-pulse">Loading data...</div>;
  const a = c?.autopsy;

  if (!c) return <div className="text-forensic-muted">Case not found.</div>;
  if (!a) {
    return (
      <div className="space-y-4">
        <div className="panel panel-pad text-forensic-muted text-sm">
          No autopsy report ingested for this case yet. Upload a PDF, image, or
          plain-text autopsy below — OCR + the autopsy analyzer will run on submit.
        </div>
        <EvidenceUpload caseId={id} defaultType="autopsy" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <EvidenceUpload caseId={id} defaultType="autopsy" />

      {/* Top: cause / manner / TOD */}
      <div className="grid lg:grid-cols-3 gap-6">
        <AIOutputCard
          title="Cause of death"
          confidence={a.cause_of_death.confidence}
          caseId={id}
          findingId="cause_of_death"
        >
          <div className="text-lg">{a.cause_of_death.value}</div>
        </AIOutputCard>
        <AIOutputCard
          title="Manner of death"
          confidence={a.manner_of_death.confidence}
          caseId={id}
          findingId="manner_of_death"
        >
          <div className="text-lg">{a.manner_of_death.value}</div>
        </AIOutputCard>
        <AIOutputCard
          title="Time of death · TOD"
          confidence={a.tod_estimate.confidence}
          reasoning={[a.tod_estimate.reasoning, ...(a.tod_estimate.caveats || [])]}
          caseId={id}
          findingId="tod_estimate"
        >
          <div className="grid grid-cols-2 gap-4">
            <Field label="Indicator window" mono>
              {a.tod_estimate.indicator_window_hours[0]}h –{' '}
              {a.tod_estimate.indicator_window_hours[1]}h
            </Field>
            <Field label="Corrected" mono>
              {a.tod_estimate.corrected_window_hours[0]}h –{' '}
              {a.tod_estimate.corrected_window_hours[1]}h
            </Field>
          </div>
          <div className="text-xs text-forensic-muted">
            Deterministic indicator model → Gemini contextual refinement.
          </div>
        </AIOutputCard>
      </div>

      {/* Postmortem indicators raw */}
      <section className="panel panel-pad">
        <div className="label mb-3">Postmortem indicators (deterministic input)</div>
        <div className="grid sm:grid-cols-3 gap-4">
          <Field label="Rigor mortis">{a.postmortem_indicators.rigor_mortis}</Field>
          <Field label="Livor mortis">{a.postmortem_indicators.livor_mortis}</Field>
          <Field label="Body temp" mono>
            {a.postmortem_indicators.body_temp_celsius != null
              ? `${a.postmortem_indicators.body_temp_celsius} °C`
              : '—'}
          </Field>
        </div>
      </section>

      {/* Injuries & toxicology */}
      <div className="grid lg:grid-cols-2 gap-6">
        <section className="panel">
          <div className="px-5 py-3 border-b border-forensic-border label">Injuries</div>
          <ul className="divide-y divide-forensic-border">
            {a.injuries.map((inj, i) => (
              <li key={i} className="px-5 py-3 flex items-start gap-3">
                <span
                  className={`chip ${
                    inj.severity === 'Severe'
                      ? 'border-forensic-critical/60 text-forensic-critical'
                      : inj.severity === 'Moderate'
                      ? 'border-forensic-warn/40 text-forensic-warn'
                      : 'border-forensic-border text-forensic-muted'
                  }`}
                >
                  {inj.severity}
                </span>
                <div className="text-sm">
                  <div>{inj.description}</div>
                  <div className="text-forensic-muted text-xs mt-0.5">{inj.location}</div>
                </div>
              </li>
            ))}
          </ul>
        </section>
        <section className="panel">
          <div className="px-5 py-3 border-b border-forensic-border label">Toxicology</div>
          <ul className="divide-y divide-forensic-border">
            {a.toxicology.map((t, i) => (
              <li key={i} className="px-5 py-3 grid grid-cols-3 gap-3 text-sm">
                <div className="font-medium">{t.substance}</div>
                <div className="mono text-forensic-accent">{t.level}</div>
                <div className="text-forensic-muted">{t.significance}</div>
              </li>
            ))}
          </ul>
        </section>
      </div>

      {/* Observations + conflicts */}
      <div className="grid lg:grid-cols-2 gap-6">
        <AIOutputCard
          title="Key observations"
          reasoning={a.reasoning_chain}
          caseId={id}
          findingId="observations"
        >
          <ul className="space-y-1.5 text-sm">
            {a.key_observations.map((o, i) => (
              <li key={i}>· {o}</li>
            ))}
          </ul>
        </AIOutputCard>

        <section className="panel">
          <div className="flex items-center gap-3 px-5 pt-4 pb-3 border-b border-forensic-border">
            <span className="chip border-forensic-warn/40 text-forensic-warn">conflicts in report</span>
            <h3 className="text-sm font-semibold">Internal contradictions</h3>
          </div>
          <ul className="px-5 py-4 space-y-2 text-sm">
            {a.conflicts_in_report.length === 0 && (
              <li className="text-forensic-muted">None detected.</li>
            )}
            {a.conflicts_in_report.map((x, i) => (
              <li key={i}>· {x}</li>
            ))}
          </ul>
        </section>
      </div>

      {/* Summary */}
      <AIOutputCard
        title="Autopsy summary"
        confidence={a.overall_confidence}
        reasoning={a.reasoning_chain}
        caseId={id}
        findingId="summary"
      >
        <p className="leading-relaxed">{a.summary}</p>
      </AIOutputCard>
    </div>
  );
}
