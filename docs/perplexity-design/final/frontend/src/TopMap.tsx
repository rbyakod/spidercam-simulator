import React from 'react';
import { TelemetryState } from './types';
import { DEFAULT_FRAME } from './frameSizing';

interface Props { telemetry: TelemetryState | null; }
const W = 200, H = 200;

export default function TopMap({ telemetry }: Props) {
  const frame = DEFAULT_FRAME;
  const pos = telemetry?.position ?? [frame.width/2, frame.height/2, frame.depth/2];
  const sx = (x: number) => (x / frame.width)  * (W - 20) + 10;
  const sz = (z: number) => (z / frame.depth)  * (H - 20) + 10;
  const corners: [number,number][] = [[0,0],[frame.width,0],[frame.width,frame.depth],[0,frame.depth]];

  return (
    <div className="panel">
      <h3>Top View (XZ)</h3>
      <svg width={W} height={H} style={{ display: 'block', background: '#0d1117',
                                          borderRadius: 4, border: '1px solid var(--border)' }}>
        {corners.map(([x,z],i) => (
          <circle key={i} cx={sx(x)} cy={sz(z)} r={5} fill="#f85149" />
        ))}
        <rect x={10} y={10} width={W-20} height={H-20} fill="none" stroke="#30363d" strokeWidth={1} />
        {corners.map(([ax,az],i) => (
          <line key={i} x1={sx(ax)} y1={sz(az)} x2={sx(pos[0])} y2={sz(pos[2])}
                stroke="#4a9eff" strokeWidth={1} strokeDasharray="4,2" />
        ))}
        <circle cx={sx(pos[0])} cy={sz(pos[2])} r={7} fill="#58a6ff" />
        <text x={sx(pos[0])+10} y={sz(pos[2])+4} fill="#c9d1d9" fontSize={10}>
          ({pos[0].toFixed(2)}, {pos[2].toFixed(2)})
        </text>
      </svg>
    </div>
  );
}
