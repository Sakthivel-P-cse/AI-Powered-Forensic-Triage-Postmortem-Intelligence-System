import { useRef, useState } from 'react';
import { api } from '../services/api.js';
import { hasRole } from '../services/auth.js';

const FILE_TYPES = [
  { value: 'autopsy', label: 'Autopsy report' },
  { value: 'cctv_log', label: 'CCTV log' },
  { value: 'gps_log', label: 'GPS log' },
  { value: 'call_log', label: 'Call log' },
  { value: 'other', label: 'Other' },
];

export default function EvidenceUpload({ caseId, defaultType = 'autopsy', onUploaded }) {
  const fileRef = useRef(null);
  const [type, setType] = useState(defaultType);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const canUpload = hasRole('INVESTIGATOR', 'ANALYST', 'ADMIN');

  if (!canUpload) {
    return (
      <div className="panel panel-pad text-forensic-muted text-xs">
        Sign in as an investigator, analyst, or admin to upload evidence.
      </div>
    );
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setResult(null);
    const file = fileRef.current?.files?.[0];
    if (!file) {
      setError('Choose a file first.');
      return;
    }
    setBusy(true);
    try {
      const out = await api.uploadEvidence({ caseId, fileType: type, file });
      setResult(out);
      onUploaded?.(out);
      if (fileRef.current) fileRef.current.value = '';
    } catch (err) {
      setError(err?.message || 'Upload failed.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel">
      <div className="px-5 py-3 border-b border-forensic-border flex items-center gap-2">
        <span className="label">Upload evidence</span>
        <span className="chip border-forensic-border text-forensic-muted ml-auto mono">
          {caseId}
        </span>
      </div>
      <form onSubmit={handleSubmit} className="px-5 py-4 space-y-3 text-sm">
        <div className="grid sm:grid-cols-3 gap-3">
          <label className="sm:col-span-1">
            <span className="label block mb-1">Type</span>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full bg-forensic-base border border-forensic-border rounded px-2 py-1.5"
            >
              {FILE_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </label>
          <label className="sm:col-span-2">
            <span className="label block mb-1">File</span>
            <input
              ref={fileRef}
              type="file"
              className="w-full text-forensic-muted file:mr-3 file:py-1.5 file:px-3 file:bg-forensic-surface file:border file:border-forensic-border file:rounded file:text-forensic-accent file:cursor-pointer"
            />
          </label>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={busy}
            className="px-4 py-1.5 rounded bg-forensic-accent/20 border border-forensic-accent/40 text-forensic-accent hover:bg-forensic-accent/30 disabled:opacity-50"
          >
            {busy ? 'Uploading…' : 'Upload'}
          </button>
          {error && <span className="text-forensic-danger text-xs">{error}</span>}
          {result && (
            <span className="text-forensic-muted text-xs mono">
              ✓ {result.bytes_uploaded} bytes · id {result.id?.slice(0, 8)}
            </span>
          )}
        </div>
        {result?.ocr_text_excerpt && (
          <div>
            <div className="label mb-1">OCR excerpt</div>
            <pre className="mono text-xs text-forensic-muted whitespace-pre-wrap bg-forensic-base/60 border border-forensic-border rounded p-3 max-h-40 overflow-auto">
              {result.ocr_text_excerpt}
            </pre>
          </div>
        )}
        {result?.autopsy_analysis && (
          <div className="text-xs text-forensic-accent">
            Autopsy analyzer ran — refresh the case to see updated findings.
          </div>
        )}
      </form>
    </section>
  );
}
