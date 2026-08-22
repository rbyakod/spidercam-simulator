import React from 'react';
import { TelemetryState } from './types';

interface Props { telemetry: TelemetryState | null; connected: boolean; }

export default function Telemetry({ telemetry, connected }: Props) {
  const pos = telemetry?.position ?? [0, 0, 0];
  const cables = telemetry?.cable_lengths ?? [0, 0, 0, 0];
  const labels = ['FL', 'FR', 'RL', 'RR'];

  return (
    <div className="panel">
      <h3>
        Telemetry
        <span className={"status-dot" + (connected ? "" : " off")} style={{ marginLeft: 8 }} />
        {connected ? "Live" : "Offline"}
      </h3>
      <div className="row">
        <label>Position</label>
        <span>X {pos[0].toFixed(3)} Y {pos[1].toFixed(3)} Z {pos[2].toFixed(3)} m</span>
      </div>
      <div className="row">
        <label>Moving</label>
        <span className={"badge " + (telemetry?.moving ? "warn" : "ok")}>
          {telemetry?.moving ? "YES" : "NO"}
        </span>
      </div>
      <div className="row">
        <label>E-Stop</label>
        <span className={"badge " + (telemetry?.e_stop ? "error" : "ok")}>
          {telemetry?.e_stop ? "ACTIVE" : "CLEAR"}
        </span>
      </div>
      <div style={{ marginTop: 8 }}>
        <label style={{ color: 'var(--text-muted)', fontSize: 11 }}>Cable Lengths (m)</label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4, marginTop: 4 }}>
          {labels.map((l, i) => (
            <div key={l} className="row" style={{ marginBottom: 0 }}>
              <label style={{ minWidth: 28 }}>{l}</label>
              <span>{cables[i]?.toFixed(4) ?? '--'}</span>
            </div>
          ))}
        </div>
      </div>
      {(telemetry?.faults?.length ?? 0) > 0 && (
        <div style={{ marginTop: 8 }}>
          {telemetry!.faults.map((fault, i) => (
            <div key={i} className="badge error" style={{ display: 'block', marginBottom: 4 }}>
              {fault.code}: {fault.message}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
