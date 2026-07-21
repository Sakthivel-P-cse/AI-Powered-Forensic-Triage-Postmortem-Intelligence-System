import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { api } from '../services/api.js';
import ContradictionMatrix from '../components/ContradictionMatrix.jsx';
import TimelineViewer from '../components/TimelineViewer.jsx';
import AIOutputCard from '../components/AIOutputCard.jsx';

export default function CorrelationMatrix() {
  const { id } = useParams();
  const [c, setC] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCase(id).then(setC).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-forensic-muted p-10 text-center animate-pulse">Loading data...</div>;
  const cor = c?.correlation;
  if (!cor) return <div className="text-forensic-muted">No correlation data.</div>;

  const counts = {
    IMPOSSIBLE: cor.contradictions.filter((x) => x.type === 'IMPOSSIBLE').length,
    SUSPICIOUS: cor.contradictions.filter((x) => x.type === 'SUSPICIOUS').length,
    UNVERIFIABLE: cor.contradictions.filter((x) => x.type === 'UNVERIFIABLE').length,
  };

  return (
    <div className="space-y-6">
      <div className="grid sm:grid-cols-3 gap-4">
        <div className="panel panel-pad">
          <div className="label">Impossible</div>
          <div className="mt-1 text-3xl font-semibold text-forensic-critical">{counts.IMPOSSIBLE}</div>
          <div className="text-xs text-forensic-muted mt-1">deterministic Haversine + travel-time</div>
        </div>
        <div className="panel panel-pad">
          <div className="label">Suspicious</div>
          <div className="mt-1 text-3xl font-semibold text-forensic-warn">{counts.SUSPICIOUS}</div>
          <div className="text-xs text-forensic-muted mt-1">within 1.5× minimum travel time</div>
        </div>
        <div className="panel panel-pad">
          <div className="label">Unverifiable</div>
          <div className="mt-1 text-3xl font-semibold text-forensic-muted">{counts.UNVERIFIABLE}</div>
          <div className="text-xs text-forensic-muted mt-1">missing location reference</div>
        </div>
      </div>

      <TimelineViewer
        events={cor.unified_timeline.map((e) => ({ ts: e.ts, source: e.source, label: e.label }))}
      />

      <section>
        <div className="flex items-center gap-3 mb-3">
          <h2 className="text-lg font-semibold">Contradiction matrix</h2>
          <span className="label">deterministic detection · Gemini explanations</span>
        </div>
        <ContradictionMatrix contradictions={cor.contradictions} />
      </section>

      <AIOutputCard title="Inconsistency summary" caseId={id} findingId="correlation_summary">
        <p className="leading-relaxed">{cor.inconsistency_summary}</p>
      </AIOutputCard>
    </div>
  );
}
