import { useState } from 'react';
import { useCaseStore } from '../store/caseStore.js';

export default function DisputeFlag({ caseId, findingId }) {
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState('');
  const dispute = useCaseStore((s) => s.disputes[caseId]?.[findingId]);
  const flag = useCaseStore((s) => s.flagDispute);

  if (dispute) {
    return (
      <span className="chip border-forensic-warn/40 text-forensic-warn bg-forensic-warn/10">
        disputed · {new Date(dispute.at).toLocaleTimeString()}
      </span>
    );
  }

  return (
    <div className="relative">
      <button onClick={() => setOpen((v) => !v)} className="text-forensic-muted hover:text-forensic-warn">
        flag as disputed
      </button>
      {open && (
        <div className="absolute right-0 bottom-full mb-2 w-72 panel panel-pad z-30 shadow-glow">
          <div className="label mb-2">Reason for dispute</div>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows="3"
            className="w-full bg-forensic-bg border border-forensic-border rounded p-2 text-sm"
            placeholder="e.g. contradicts witness statement at 02:30..."
          />
          <div className="flex gap-2 mt-2 justify-end">
            <button className="btn-ghost text-xs" onClick={() => setOpen(false)}>
              Cancel
            </button>
            <button
              className="btn-danger text-xs"
              disabled={!reason.trim()}
              onClick={() => {
                flag(caseId, findingId, reason.trim());
                setOpen(false);
                setReason('');
              }}
            >
              Flag finding
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
