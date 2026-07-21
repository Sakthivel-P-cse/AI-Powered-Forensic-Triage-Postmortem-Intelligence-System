// Arc-style risk gauge with LOW → CRITICAL color band.
// score: 0..100
export default function RiskGauge({ score = 0, level = 'LOW', size = 220 }) {
  const s = Math.max(0, Math.min(100, score));
  const r = (size - 24) / 2;
  const cx = size / 2;
  const cy = size / 2 + 6;
  const start = Math.PI; // 180°
  const end = 2 * Math.PI; // 360° (top right)
  const t = start + (end - start) * (s / 100);

  const arcPath = (from, to) => {
    const x1 = cx + r * Math.cos(from);
    const y1 = cy + r * Math.sin(from);
    const x2 = cx + r * Math.cos(to);
    const y2 = cy + r * Math.sin(to);
    const large = to - from > Math.PI ? 1 : 0;
    return `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`;
  };

  const color =
    level === 'CRITICAL'
      ? '#FF2E5B'
      : level === 'HIGH'
      ? '#FF5C7A'
      : level === 'MEDIUM'
      ? '#FFB454'
      : '#5CFFB1';

  // segment colors along the arc
  const segs = [
    { f: 0, to: 0.30, c: '#5CFFB1' },
    { f: 0.30, to: 0.60, c: '#FFB454' },
    { f: 0.60, to: 0.80, c: '#FF5C7A' },
    { f: 0.80, to: 1.00, c: '#FF2E5B' },
  ];

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size * 0.66} viewBox={`0 0 ${size} ${size * 0.66}`}>
        <defs>
          <filter id="g-glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2.5" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        {/* track */}
        <path
          d={arcPath(start, end)}
          stroke="#1F2A37"
          strokeWidth="14"
          strokeLinecap="round"
          fill="none"
        />
        {/* colored band */}
        {segs.map((seg) => (
          <path
            key={seg.f}
            d={arcPath(start + (end - start) * seg.f, start + (end - start) * seg.to)}
            stroke={seg.c}
            strokeOpacity="0.35"
            strokeWidth="14"
            strokeLinecap="butt"
            fill="none"
          />
        ))}
        {/* progress */}
        <path
          d={arcPath(start, t)}
          stroke={color}
          strokeWidth="14"
          strokeLinecap="round"
          fill="none"
          filter="url(#g-glow)"
        />
        {/* needle */}
        <line
          x1={cx}
          y1={cy}
          x2={cx + (r - 6) * Math.cos(t)}
          y2={cy + (r - 6) * Math.sin(t)}
          stroke={color}
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <circle cx={cx} cy={cy} r="4" fill={color} />
      </svg>
      <div className="-mt-6 text-center">
        <div className="text-5xl mono font-semibold" style={{ color }}>
          {s}
        </div>
        <div
          className="text-[11px] uppercase tracking-[0.22em] mono mt-1"
          style={{ color }}
        >
          {level}
        </div>
      </div>
    </div>
  );
}
