const STYLE = {
  LOW: 'border-forensic-ok/40 text-forensic-ok bg-forensic-ok/10',
  MEDIUM: 'border-forensic-warn/40 text-forensic-warn bg-forensic-warn/10',
  HIGH: 'border-forensic-danger/40 text-forensic-danger bg-forensic-danger/10',
  CRITICAL: 'border-forensic-critical/60 text-forensic-critical bg-forensic-critical/15',
};

export default function RiskBadge({ level = 'LOW', score }) {
  return (
    <span className={`chip ${STYLE[level] || STYLE.LOW}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {level}
      {score != null && <span className="ml-1 mono opacity-80">{score}</span>}
    </span>
  );
}
