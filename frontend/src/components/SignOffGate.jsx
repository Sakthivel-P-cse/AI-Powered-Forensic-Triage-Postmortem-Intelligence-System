import { useState } from 'react';
import { currentUser } from '../services/auth.js';
import { useCaseStore } from '../store/caseStore.js';

export default function SignOffGate({ caseId }) {
  const user = currentUser();
  const signoff = useCaseStore((s) => s.signoffs[caseId]);
  const sign = useCaseStore((s) => s.signOff);
  const [confirm, setConfirm] = useState(false);

  const isAnalyst = user?.role === 'ANALYST' || user?.role === 'ADMIN';

  if (signoff) {
    return (
      <div className="panel panel-pad border-forensic-ok/40 bg-forensic-ok/5">
        <div className="flex items-center gap-3">
          <span className="chip border-forensic-ok/40 text-forensic-ok">Signed off</span>
          <div className="text-sm">
            By <span className="mono text-forensic-text">{signoff.analyst}</span>{' '}
            on{' '}
            <span className="mono text-forensic-muted">
              {new Date(signoff.at).toLocaleString()}
            </span>
          </div>
          <div className="ml-auto">
            <button className="btn-primary text-sm" onClick={() => alert('Export simulated.')}>
              Export final report
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="panel panel-pad border-forensic-warn/40 bg-forensic-warn/5">
      <div className="flex items-start gap-4">
        <span className="chip border-forensic-warn/40 text-forensic-warn">Locked · DRAFT</span>
        <div className="text-sm flex-1">
          <div className="font-medium">Forensic Analyst sign-off required.</div>
          <div className="text-forensic-muted mt-1">
            AI-generated reports cannot be exported until a qualified analyst signs off.
            The signature is immutable and audit-logged.
          </div>
        </div>
        {!isAnalyst ? (
          <span className="chip border-forensic-border text-forensic-muted">
            requires ANALYST role
          </span>
        ) : !confirm ? (
          <button className="btn-primary" onClick={() => setConfirm(true)}>
            Sign off as analyst
          </button>
        ) : (
          <div className="flex gap-2">
            <button className="btn-ghost text-sm" onClick={() => setConfirm(false)}>
              Cancel
            </button>
            <button
              className="btn-primary text-sm"
              onClick={() => {
                sign(caseId, user.email);
                setConfirm(false);
              }}
            >
              Confirm signature · {user.email}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
