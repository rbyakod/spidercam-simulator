import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { MotionProfile } from './types';

export default function ProfileSelector() {
  const [profiles, setProfiles] = useState<MotionProfile[]>([]);
  const [selected, setSelected] = useState('');

  useEffect(() => {
    axios.get('/api/profiles').then(r => {
      const list = r.data.profiles ?? [];
      setProfiles(list);
      if (list.length) setSelected(list[0].name);
    });
  }, []);

  const apply = async () => {
    const p = profiles.find(x => x.name === selected);
    if (!p) return;
    await axios.post('/api/profiles', p);
  };

  const current = profiles.find(p => p.name === selected);

  return (
    <div className="panel">
      <h3>Motion Profile</h3>
      <div className="row">
        <select value={selected} onChange={e => setSelected(e.target.value)}>
          {profiles.map(p => <option key={p.name} value={p.name}>{p.name}</option>)}
        </select>
        <button className="btn" onClick={apply}>Apply</button>
      </div>
      {current && (
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
          {current.description} | Speed: {current.max_speed} m/s | Accel: {current.max_accel} m/s2
        </div>
      )}
    </div>
  );
}
