import React, { useState } from 'react';
import axios from 'axios';

const STEPS = [
  'Move to centre of frame',
  'Ensure all cables are taut',
  'Measure each cable length with a tape measure',
  'Enter measurements below',
  'Click Compute Offsets',
];

export default function CalibrationWizard() {
  const [step, setStep] = useState(0);
  const [lengths, setLengths] = useState(['','','','']);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');
  const labels = ['FL','FR','RL','RR'];

  const next = () => setStep(s => Math.min(s + 1, STEPS.length - 1));
  const back = () => setStep(s => Math.max(s - 1, 0));

  const compute = async () => {
    try {
      await axios.post('/api/calibrate', { measured_lengths: lengths.map(Number) });
      setDone(true);
    } catch (e: any) {
      setError(e.response?.data?.detail ?? 'Calibration failed');
    }
  };

  if (done) return (
    <div className="panel">
      <h3>Calibration Wizard</h3>
      <div className="badge ok">Calibration complete!</div>
    </div>
  );

  return (
    <div className="panel">
      <h3>Calibration Wizard - Step {step + 1}/{STEPS.length}</h3>
      <p style={{ fontSize: 12, marginBottom: 10, color: 'var(--text)' }}>{STEPS[step]}</p>
      {step === 3 && labels.map((l, i) => (
        <div className="row" key={l}>
          <label>{l}</label>
          <input type="number" step="0.001" value={lengths[i]}
                 onChange={e => { const c=[...lengths]; c[i]=e.target.value; setLengths(c); }} />
          <span style={{fontSize:11,color:'var(--text-muted)'}}>m</span>
        </div>
      ))}
      {error && <div className="badge error" style={{ marginBottom: 6 }}>{error}</div>}
      <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
        <button className="btn" onClick={back} disabled={step === 0}>Back</button>
        {step < STEPS.length - 1
          ? <button className="btn primary" onClick={next}>Next</button>
          : <button className="btn primary" onClick={compute}>Compute Offsets</button>
        }
      </div>
    </div>
  );
}
