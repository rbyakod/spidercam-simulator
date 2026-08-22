import React, { useState, useCallback } from 'react';
import axios from 'axios';

const STEP = 0.05;

export default function Joystick() {
  const [busy, setBusy] = useState(false);

  const jog = useCallback(async (axis: number, dir: 1 | -1) => {
    if (busy) return;
    setBusy(true);
    try {
      await axios.post('/api/jog', { axis, distance: STEP * dir, speed: 0.1 });
    } catch (e) {
      console.error(e);
    } finally {
      setBusy(false);
    }
  }, [busy]);

  const estop = async () => { await axios.post('/api/estop'); };
  const clearFault = async () => { await axios.post('/api/fault/clear'); };
  const btn = (label: string, axis: number, dir: 1 | -1) => (
    <button className="btn" onClick={() => jog(axis, dir)} disabled={busy}>{label}</button>
  );

  return (
    <div className="panel">
      <h3>Jog Controls</h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 4,
                    maxWidth: 160, margin: '0 auto' }}>
        <div />{btn('Y+', 1, 1)}<div />
        {btn('X-', 0, -1)}
        <div style={{ display:'flex', alignItems:'center', justifyContent:'center',
                      fontSize: 11, color: 'var(--text-muted)' }}>XY</div>
        {btn('X+', 0, 1)}
        <div />{btn('Y-', 1, -1)}<div />
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 8, justifyContent: 'center' }}>
        {btn('Z+', 2, 1)}{btn('Z-', 2, -1)}
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 10, justifyContent: 'center' }}>
        <button className="btn danger" onClick={estop}>E-STOP</button>
        <button className="btn" onClick={clearFault}>Clear</button>
      </div>
    </div>
  );
}
