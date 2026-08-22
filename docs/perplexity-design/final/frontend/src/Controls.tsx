import React from 'react';
import axios from 'axios';

export default function Controls() {
  const estop = () => axios.post('/api/estop');
  const clear = () => axios.post('/api/fault/clear');
  const home  = () => axios.post('/api/home');

  return (
    <div className="panel">
      <h3>Controls</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        <button className="btn danger" onClick={estop} style={{ width: '100%' }}>
          EMERGENCY STOP
        </button>
        <button className="btn" onClick={clear} style={{ width: '100%' }}>
          Clear Faults
        </button>
        <button className="btn" onClick={home} style={{ width: '100%' }}>
          Run Homing Sequence
        </button>
      </div>
    </div>
  );
}
