import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface GPIOAxis {
  name: string;
  step_pin: number;
  dir_pin: number;
  enable_pin?: number;
}

interface GPIOMap {
  axes?: GPIOAxis[];
  limit_pins?: number[];
}

export default function HardwareGatePanel() {
  const [gpio, setGpio] = useState<GPIOMap>({});
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    axios.get('/api/gpio').then(r => setGpio(r.data));
  }, []);

  const save = async () => {
    await axios.post('/api/gpio', gpio);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="panel">
      <h3>GPIO Map</h3>
      {gpio.axes?.map((ax, i) => (
        <div key={i} style={{ fontSize: 11, marginBottom: 4 }}>
          <strong>{ax.name}</strong>: STEP={ax.step_pin} DIR={ax.dir_pin}
          {ax.enable_pin !== undefined && <> EN={ax.enable_pin}</>}
        </div>
      ))}
      {gpio.limit_pins && (
        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
          Limit pins: {gpio.limit_pins.join(', ')}
        </div>
      )}
      <button className="btn" onClick={save} style={{ marginTop: 8, width: '100%' }}>
        {saved ? 'Saved!' : 'Save GPIO Map'}
      </button>
      <p style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
        Edit data/spiderpi.yaml to change pin assignments, then restart backend.
      </p>
    </div>
  );
}
