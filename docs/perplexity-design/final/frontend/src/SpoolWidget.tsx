import React from 'react';

interface Props { lengths: number[]; }
const LABELS = ['FL','FR','RL','RR'];
const R = 30;

export default function SpoolWidget({ lengths }: Props) {
  const max = Math.max(...lengths, 0.01);
  return (
    <div className="panel">
      <h3>Spool Visualiser</h3>
      <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
        {LABELS.map((label, i) => {
          const pct = lengths[i] / max;
          const total = 2 * Math.PI * R;
          const offset = total * (1 - pct);
          return (
            <div key={label} style={{ textAlign: 'center' }}>
              <svg width={80} height={80}>
                <circle cx={40} cy={40} r={R} fill="none" stroke="#21262d" strokeWidth={10} />
                <circle cx={40} cy={40} r={R} fill="none" stroke="#58a6ff" strokeWidth={10}
                        strokeDasharray={total + ' ' + total}
                        strokeDashoffset={offset}
                        strokeLinecap="round"
                        transform="rotate(-90 40 40)" />
                <text x={40} y={44} textAnchor="middle" fill="#c9d1d9" fontSize={10}>
                  {lengths[i]?.toFixed(3) ?? '-'}m
                </text>
              </svg>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{label}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
