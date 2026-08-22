import React, { useState } from 'react';
import axios from 'axios';
import { HomingStatus } from './types';

interface Props { homing: HomingStatus | undefined; }
const LABELS = ['FL','FR','RL','RR'];

export default function HomingPanel({ homing }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const runHoming = async () => {
    setBusy(true);
    setError('');
    try {
      await axios.post('/api/home');
    } catch (e: any) {
      setError(e.response?.data?.detail ?? 'Homing failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="panel">
      <h3>Homing</h3>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 8 }}>
        {LABELS.map((l, i) => (
          <span key={l} className={"badge " + (homing?.homed[i] ? "ok" : "warn")}>
            {l} {homing?.homed[i] ? "[OK]" : "[ ]"}
          </span>
        ))}
      </div>
      <button className="btn primary" onClick={runHoming} disabled={busy}
              style={{ width: '100%' }}>
        {busy ? 'Homing...' : homing?.all_homed ? 'Re-Home' : 'Run Homing'}
      </button>
      {error && <div className="badge error" style={{ marginTop: 6 }}>{error}</div>}
    </div>
  );
}
