import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { MotionProfile } from './types';

export default function ProfileManager() {
  const [profiles, setProfiles] = useState<MotionProfile[]>([]);
  const [form, setForm] = useState<Partial<MotionProfile>>({
    name: '', max_speed: 0.3, max_accel: 0.6, description: ''
  });

  const load = () => axios.get('/api/profiles').then(r => setProfiles(r.data.profiles ?? []));
  useEffect(() => { load(); }, []);

  const save = async () => {
    await axios.post('/api/profiles', form);
    load();
  };

  const del = async (name: string) => {
    await axios.delete('/api/profiles/' + name);
    load();
  };

  return (
    <div className="panel">
      <h3>Manage Profiles</h3>
      {profiles.map(p => (
        <div key={p.name} className="row" style={{ justifyContent: 'space-between' }}>
          <span>{p.name}</span>
          <button className="btn danger" onClick={() => del(p.name)}
                  style={{ padding: '2px 8px', fontSize: 11 }}>Del</button>
        </div>
      ))}
      <div style={{ borderTop: '1px solid var(--border)', marginTop: 8, paddingTop: 8 }}>
        <div className="row">
          <label>Name</label>
          <input value={form.name ?? ''} onChange={e => setForm(f => ({...f, name: e.target.value}))} />
        </div>
        <div className="row">
          <label>Speed</label>
          <input type="number" step="0.05" value={form.max_speed ?? 0.3}
                 onChange={e => setForm(f => ({...f, max_speed: +e.target.value}))} />
        </div>
        <div className="row">
          <label>Accel</label>
          <input type="number" step="0.1" value={form.max_accel ?? 0.6}
                 onChange={e => setForm(f => ({...f, max_accel: +e.target.value}))} />
        </div>
        <button className="btn primary" onClick={save} style={{ width: '100%', marginTop: 4 }}>
          Save Profile
        </button>
      </div>
    </div>
  );
}
