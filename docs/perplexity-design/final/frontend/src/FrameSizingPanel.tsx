import React, { useState } from 'react';
import axios from 'axios';
import { DEFAULT_FRAME, validateFrame } from './frameSizing';
import { FrameDimensions } from './types';

export default function FrameSizingPanel() {
  const [frame, setFrame] = useState<FrameDimensions>(DEFAULT_FRAME);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  const apply = async () => {
    const err = validateFrame(frame);
    if (err) { setError(err); return; }
    setError('');
    try {
      await axios.post('/api/frame', frame);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e: any) {
      setError(e.response?.data?.detail ?? 'Failed to save frame');
    }
  };

  return (
    <div className="panel">
      <h3>Frame Sizing</h3>
      {(['width','height','depth'] as const).map(dim => (
        <div className="row" key={dim}>
          <label style={{ minWidth: 52 }}>
            {dim.charAt(0).toUpperCase() + dim.slice(1)}
          </label>
          <input type="number" step="0.1" min="0.3" max="10"
                 value={frame[dim]}
                 onChange={e => setFrame(f => ({ ...f, [dim]: parseFloat(e.target.value) }))} />
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>m</span>
        </div>
      ))}
      {error && <div className="badge error" style={{ marginBottom: 6 }}>{error}</div>}
      <button className="btn primary" onClick={apply} style={{ width: '100%', marginTop: 4 }}>
        {saved ? 'Saved!' : 'Apply'}
      </button>
    </div>
  );
}
