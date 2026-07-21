import { useMemo, useState } from 'react';

// Horizontal multi-source timeline with zoom.
// events: [{ ts: ISO, source: 'CCTV'|'GPS'|'CALL'|..., label, severity?: 'LOW'|'MEDIUM'|'HIGH'|'CRITICAL' }]
const SOURCE_COLORS = {
  CCTV: '#00C8FF',
  GPS: '#5CFFB1',
  CALL: '#FFB454',
  AUTOPSY: '#FF5C7A',
  OTHER: '#7A8899',
};

export default function TimelineViewer({ events = [], height = 220 }) {
  const [zoom, setZoom] = useState(1);

  const { items, t0, t1 } = useMemo(() => {
    if (!events.length) return { items: [], t0: 0, t1: 1 };
    const ts = events.map((e) => +new Date(e.ts));
    const t0 = Math.min(...ts);
    const t1 = Math.max(...ts);
    const span = Math.max(1, t1 - t0);
    const items = events.map((e, i) => ({
      ...e,
      x: ((+new Date(e.ts) - t0) / span) * 100,
      _i: i,
    }));
    return { items, t0, t1 };
  }, [events]);

  const sources = useMemo(
    () => Array.from(new Set(items.map((e) => e.source))),
    [items]
  );

  if (!items.length)
    return (
      <div className="panel panel-pad text-forensic-muted text-sm">
        No timeline events.
      </div>
    );

  const fmt = (ms) =>
    new Date(ms).toLocaleString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      day: '2-digit',
      month: 'short',
    });

  return (
    <div className="panel">
      <div className="flex items-center gap-3 px-5 py-3 border-b border-forensic-border">
        <span className="label">Unified timeline</span>
        <div className="flex gap-2 ml-2">
          {sources.map((s) => (
            <span key={s} className="chip border-forensic-border text-forensic-muted">
              <span
                className="w-2 h-2 rounded-full"
                style={{ background: SOURCE_COLORS[s] || SOURCE_COLORS.OTHER }}
              />
              {s}
            </span>
          ))}
        </div>
        <div className="ml-auto flex items-center gap-2 text-xs text-forensic-muted mono">
          <button className="btn-ghost text-xs px-2 py-1" onClick={() => setZoom((z) => Math.max(1, z / 1.5))}>−</button>
          <span>{zoom.toFixed(1)}×</span>
          <button className="btn-ghost text-xs px-2 py-1" onClick={() => setZoom((z) => Math.min(8, z * 1.5))}>+</button>
        </div>
      </div>

      <div className="overflow-x-auto" style={{ height }}>
        <div
          className="relative gridline"
          style={{ width: `${100 * zoom}%`, height: '100%' }}
        >
          {/* source lanes */}
          {sources.map((s, idx) => {
            const top = 30 + idx * 42;
            return (
              <div key={s} className="absolute left-0 right-0" style={{ top }}>
                <div className="h-px bg-forensic-line/70" />
                <div className="absolute -top-3 left-2 label" style={{ color: SOURCE_COLORS[s] }}>
                  {s}
                </div>
              </div>
            );
          })}
          {/* events */}
          {items.map((e) => {
            const lane = sources.indexOf(e.source);
            const top = 30 + lane * 42 - 10;
            const color = SOURCE_COLORS[e.source] || SOURCE_COLORS.OTHER;
            return (
              <div
                key={e._i}
                className="absolute group"
                style={{ left: `${e.x}%`, top }}
              >
                <div
                  className="w-3 h-3 rounded-full -ml-1.5 ring-2 ring-forensic-bg"
                  style={{ background: color, boxShadow: `0 0 14px ${color}55` }}
                />
                <div
                  className="hidden group-hover:block absolute z-10 mt-1 -translate-x-1/2 left-0 panel panel-pad text-xs whitespace-nowrap shadow-glow"
                  style={{ minWidth: 220 }}
                >
                  <div className="mono text-forensic-accent">{fmt(+new Date(e.ts))}</div>
                  <div>{e.label}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      <div className="flex justify-between px-5 py-2 border-t border-forensic-border text-[11px] mono text-forensic-muted">
        <span>{fmt(t0)}</span>
        <span>{fmt(t1)}</span>
      </div>
    </div>
  );
}
