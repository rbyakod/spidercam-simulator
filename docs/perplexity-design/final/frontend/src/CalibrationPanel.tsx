import React, { useState } from 'react';
import axios from 'axios';

export default function CalibrationPanel() {
  const [lengths, setLengths] = useState(['','','','']);
  const [result, setResult] = useState<any>(null);
  const labels = ['FL','FR','RL','RR'];

  const calibrate = async () => {
    try {
      const r = await axios.post('/api/calibrate', {
        measured_lengths: lengths.map(Number),
      });
      setResult(r.data);
    } catch (e: any) {
      setResult({ error: e.response?.data?.detail ?? e.message });
    }
  };

  return (
    <div className="panel">
      <h3>Calibration</h3>
      <p style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 8 }}>
        Enter measured cable lengths at reference position (centre of frame).
      </p>
      {labels.map((l, i) => (
        <div className="row" key={l}>
          <label>{l} (m)</label>
          <input type="number" step="0.001"
                 value={lengths[i]}
                 onChange={e => {
                   const copy = [...lengths];
                   copy[i] = e.target.value;
                   setLengths(copy);
                 }} />
        </div>
      ))}
      <button className="btn primary" onClick={calibrate}
              style={{ width: '100%', marginTop: 4 }}>
        Compute Offsets
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
