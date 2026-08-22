import { SpiderState } from "../types";

export function TopMap({ state, onMove }: { state: SpiderState | null; onMove: (x: number, y: number) => void }) {
  if (!state) return <div className="panel"><h3>XY Map</h3><p>Loading map...</p></div>;
  const width = 280, height = 280;
  const [xmin, xmax] = state.bounds.x;
  const [ymin, ymax] = state.bounds.y;
  const xToPx = (x: number) => ((x - xmin) / (xmax - xmin)) * width;
  const yToPx = (y: number) => ((y - ymin) / (ymax - ymin)) * height;
  const pxToX = (px: number) => xmin + (px / width) * (xmax - xmin);
  const pxToY = (py: number) => ymin + (py / height) * (ymax - ymin);
  return (
    <div className="panel">
      <h3>XY Map</h3>
      <svg
        className="map"
        width={width} height={height}
        style={{ display: "block", margin: "0 auto", cursor: "crosshair" }}
        onClick={(e) => {
          const rect = (e.target as SVGElement).getBoundingClientRect();
          onMove(pxToX(e.clientX - rect.left), pxToY(e.clientY - rect.top));
        }}
      >
        <rect width={width} height={height} fill="#0b1020" stroke="#334155" />
        {/* Anchor markers */}
        {Object.entries(state.anchors).map(([k, [ax, , ay]]) => (
          <g key={k}>
            <rect x={xToPx(ax)-8} y={yToPx(ay)-8} width={16} height={16} fill="#475569" rx={3}/>
            <text x={xToPx(ax)} y={yToPx(ay)+5} textAnchor="middle" fill="#e2e8f0" fontSize={10}>{k}</text>
          </g>
        ))}
        {/* Trail */}
        {state.trail && state.trail.length > 1 && (
          <polyline
            points={state.trail.map(p => `${xToPx(p.x)},${yToPx(p.y)}`).join(" ")}
            fill="none" stroke="#f59e0b" strokeWidth={1} opacity={0.5}
          />
        )}
        {/* Target */}
        <circle cx={xToPx(state.target.x)} cy={yToPx(state.target.y)} r={6} fill="none" stroke="#22d3ee" strokeWidth={1.5} strokeDasharray="3,3"/>
        {/* Position */}
        <circle cx={xToPx(state.position.x)} cy={yToPx(state.position.y)} r={8}
          fill={state.estop ? "#dc2626" : "#f59e0b"} opacity={0.9}/>
      </svg>
      <p className="hint">Click map to move target at current Z.</p>
    </div>
  );
}
