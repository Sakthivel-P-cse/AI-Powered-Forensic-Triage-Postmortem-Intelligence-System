const TYPE_STYLE = {
  IMPOSSIBLE: { ring: 'border-forensic-critical/60', tint: 'bg-forensic-critical/10', text: 'text-forensic-critical' },
  SUSPICIOUS: { ring: 'border-forensic-warn/40', tint: 'bg-forensic-warn/10', text: 'text-forensic-warn' },
  UNVERIFIABLE: { ring: 'border-forensic-border', tint: 'bg-forensic-surface/60', text: 'text-forensic-muted' },
};

const PRIORITY_STYLE = {
  CRITICAL: 'text-forensic-critical',
  HIGH: 'text-forensic-danger',
  MEDIUM: 'text-forensic-warn',
  LOW: 'text-forensic-muted',
};

function fmtTs(s) {
  return new Date(s).toLocaleString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: 'short',
  });
}

export default function ContradictionMatrix({ contradictions = [] }) {
  if (!contradictions.length)
    return (
      <div className="panel panel-pad text-forensic-muted text-sm">
        No contradictions detected.
      </div>
    );

  return (
    <div className="grid gap-3">
      {contradictions.map((c) => {
        const s = TYPE_STYLE[c.type] || TYPE_STYLE.UNVERIFIABLE;
        return (
          <div key={c.id} className={`panel border-2 ${s.ring} ${s.tint}`}>
            <div className="flex items-center gap-3 px-5 pt-4 pb-3 border-b border-forensic-border/60">
              <span className={`chip ${s.ring} ${s.text}`}>{c.type}</span>
              <span className="text-sm font-semibold tracking-wide">
                Contradiction #{c.id}
              </span>
              <span className="ml-auto label">
                priority{' '}
                <span className={`mono ml-1 ${PRIORITY_STYLE[c.investigative_priority]}`}>
                  {c.investigative_priority}
                </span>
              </span>
            </div>
            <div className="grid md:grid-cols-2 gap-0 divide-x divide-forensic-border/60">
              <div className="p-5">
                <div className="label">Source A · {c.source_a.kind}</div>
                <div className="mono text-forensic-accent text-sm mt-1">{fmtTs(c.source_a.ts)}</div>
                <div className="text-sm text-forensic-text/90 mt-0.5">{c.source_a.loc}</div>
              </div>
              <div className="p-5">
                <div className="label">Source B · {c.source_b.kind}</div>
                <div className="mono text-forensic-accent text-sm mt-1">{fmtTs(c.source_b.ts)}</div>
                <div className="text-sm text-forensic-text/90 mt-0.5">{c.source_b.loc}</div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-0 divide-x divide-forensic-border/60 border-t border-forensic-border/60 text-sm">
              <div className="p-4">
                <div className="label">Δ time</div>
                <div className="mono mt-1">{c.time_delta_min.toFixed(1)} min</div>
              </div>
              <div className="p-4">
                <div className="label">Δ distance</div>
                <div className="mono mt-1">{c.distance_km.toFixed(2)} km</div>
              </div>
              <div className="p-4">
                <div className="label">Implied speed</div>
                <div className="mono mt-1">
                  {c.time_delta_min > 0
                    ? `${((c.distance_km / (c.time_delta_min / 60)) || 0).toFixed(0)} km/h`
                    : '—'}
                </div>
              </div>
            </div>
            <div className="px-5 py-4 border-t border-forensic-border/60 text-sm">
              {c.explanation}
            </div>
          </div>
        );
      })}
    </div>
  );
}
