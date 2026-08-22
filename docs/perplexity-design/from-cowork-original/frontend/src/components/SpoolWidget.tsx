export function SpoolWidget({ label, angle, tension, current, margin, hot }:
  { label: string; angle: number; tension: number; current: number; margin: number; hot: boolean }) {
  const color = hot ? "#fca5a5" : margin > 1.5 ? "#86efac" : "#fbbf24";
  return (
    <div className="spoolCard">
      <div className="spoolTitle">{label}</div>
      <div className="spoolFace">
        <div className="spoolRotor" style={{ borderColor: color }}>
          <div className="spoolMark" style={{ transform: `translateY(-50%) rotate(${angle}rad)` }} />
        </div>
      </div>
      <div className="spoolStats">
        <div>T {tension.toFixed(1)} N</div>
        <div>I {current.toFixed(2)} A</div>
        <div style={{ color }}>M {margin.toFixed(2)}</div>
      </div>
    </div>
  );
}
