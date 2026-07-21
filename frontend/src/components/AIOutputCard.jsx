import DisputeFlag from './DisputeFlag.jsx';

// Wraps any AI-generated finding with the mandatory provenance label,
// reasoning chain, and dispute control.
export default function AIOutputCard({
  title,
  confidence,
  reasoning = [],
  caseId,
  findingId,
  children,
  right,
}) {
  const conf =
    confidence == null
      ? null
      : typeof confidence === 'number'
      ? `${(confidence * 100).toFixed(0)}%`
      : confidence;

  return (
    <section className="panel">
      <div className="flex items-center gap-3 px-5 pt-4 pb-3 border-b border-forensic-border">
        <span className="chip border-forensic-accent/40 text-forensic-accent">
          AI-assisted
        </span>
        <h3 className="text-sm font-semibold tracking-wide">{title}</h3>
        {conf && (
          <span className="ml-auto label">
            confidence <span className="text-forensic-text mono ml-1">{conf}</span>
          </span>
        )}
        {right}
      </div>
      <div className="panel-pad space-y-4">{children}</div>
      {reasoning.length > 0 && (
        <details className="border-t border-forensic-border">
          <summary className="px-5 py-2.5 cursor-pointer text-xs uppercase tracking-[0.18em] text-forensic-muted hover:text-forensic-text mono">
            reasoning chain ({reasoning.length})
          </summary>
          <ol className="px-5 pb-4 space-y-1.5 text-sm text-forensic-text/90">
            {reasoning.map((r, i) => (
              <li key={i} className="flex gap-3">
                <span className="mono text-forensic-accent text-xs pt-0.5">{String(i + 1).padStart(2, '0')}</span>
                <span>{r}</span>
              </li>
            ))}
          </ol>
        </details>
      )}
      <div className="px-5 py-2.5 border-t border-forensic-border bg-forensic-bg/40 flex items-center justify-between text-[11px] text-forensic-muted mono">
        <span>requires human review · auditable</span>
        {caseId && findingId && <DisputeFlag caseId={caseId} findingId={findingId} />}
      </div>
    </section>
  );
}
