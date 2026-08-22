import React, { useState } from 'react';
import axios from 'axios';

export default function PhysicsPanel() {
  const [target, setTarget] = useState({ x: '0.5', y: '0.8', z: '0.5' });
  const [payload, setPayload] = useState('0.5');
  const [result, setResult] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  const move = async () => {
    setBusy(true);
    try {
      const r = await axios.post('/api/move', {
        x: parseFloat(target.x),
        y: parseFloat(target.y),
        z: parseFloat(target.z),
        payload_kg: parseFloat(payload),
      });
      setResult(r.data);
    } catch (e: any) {
      setResult({ error: e.response?.data?.detail ?? e.message });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="panel">
      <h3>Move To Position</h3>
      {(['x','y','z'] as const).map(ax => (
        <div className="row" key={ax}>
          <label>{ax.toUpperCase()} (m)</label>
          <input type="number" step="0.01"
                 value={target[ax]}
                 onChange={e => setTarget(t => ({...t, [ax]: e.target.value}))} />
        </div>
      ))}
      <div className="row">
        <label>kg</label>
        <input type="number" step="0.1" value={payload}
               onChange={e => setPayload(e.target.value)} />
      </div>
      <button className="btn primary" onClick={move} disabled={busy}
              style={{ width: '100%', marginTop: 4 }}>
        {busy ? 'Moving...' : 'Move'}
      </button>
      {result && (
        <pre style={{ fontSize: 10, marginTop: 8, overflowX: 'auto',
                      color: result.error ? 'var(--danger)' : 'var(--success)' }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
