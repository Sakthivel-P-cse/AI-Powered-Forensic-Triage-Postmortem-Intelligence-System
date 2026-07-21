export default function EvidenceCard({ icon, label, value, sub, accent = false }) {
  return (
    <div className={`panel panel-pad ${accent ? 'shadow-glow' : ''}`}>
      <div className="flex items-center gap-2 label">
        {icon} {label}
      </div>
      <div className={`mt-2 text-2xl font-semibold ${accent ? 'text-forensic-accent' : ''}`}>
        {value}
      </div>
      {sub && <div className="text-xs text-forensic-muted mt-1">{sub}</div>}
    </div>
  );
}
