import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { api } from '../services/api.js';
import RiskGauge from '../components/RiskGauge.jsx';
import AIOutputCard from '../components/AIOutputCard.jsx';

export default function RiskView() {
  const { id } = useParams();
  const [c, setC] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCase(id).then(setC).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-forensic-muted p-10 text-center animate-pulse">Loading data...</div>;
  if (!c) return null;
  const r = c.risk;

  return (
    <div className="space-y-6">
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="panel panel-pad lg:col-span-1 flex flex-col items-center">
          <RiskGauge score={r.score} level={r.level} />
          <div className="mt-4 text-xs text-forensic-muted text-center">
            Score is computed by deterministic weighted rules — Gemini cannot alter it.
          </div>
        </div>

        <section className="panel lg:col-span-2">
          <div className="px-5 py-3 border-b border-forensic-border label">Factor breakdown</div>
          <ul className="divide-y divide-forensic-border">
            {r.factors.map((f, i) => {
              const pct = Math.round((f.value / f.max) * 100);
              return (
                <li key={i} className="px-5 py-3">
                  <div className="flex justify-between text-sm">
                    <span>{f.name}</span>
                    <span className="mono text-forensic-text">
                      {f.value} <span className="text-forensic-muted">/ {f.max}</span>
                    </span>
                  </div>
                  <div className="mt-2 h-1.5 bg-forensic-bg rounded overflow-hidden">
                    <div
                      className="h-full"
                      style={{
                        width: `${pct}%`,
                        background:
                          pct >= 80
                            ? '#FF2E5B'
                            : pct >= 60
                            ? '#FF5C7A'
                            : pct >= 30
                            ? '#FFB454'
                            : '#5CFFB1',
                      }}
                    />
                  </div>
                  <div className="text-xs text-forensic-muted mt-1">{f.note}</div>
                </li>
              );
            })}
          </ul>
        </section>
      </div>

      <AIOutputCard title="Investigation briefing" caseId={id} findingId="risk_briefing">
        <p className="leading-relaxed">{r.briefing}</p>
        <div className="grid md:grid-cols-2 gap-6 mt-4">
          <div>
            <div className="label mb-2">Recommended next steps</div>
            <ol className="space-y-1.5 text-sm">
              {r.next_steps.map((s, i) => (
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
              {r.caveats.map((s, i) => (
                <li key={i}>· {s}</li>
              ))}
            </ul>
          </div>
        </div>
      </AIOutputCard>
    </div>
  );
}
