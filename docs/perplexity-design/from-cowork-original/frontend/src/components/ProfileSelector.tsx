import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export function ProfileSelector() {
  const [profiles, setProfiles] = useState<Record<string, any>>({});
  const [selected, setSelected] = useState("");
  const [status, setStatus] = useState("");

  const load = async () => {
    const r = await fetch(`${API}/profiles`);
    const d = await r.json();
    setProfiles(d.profiles || {});
  };

  useEffect(() => { load(); }, []);

  const apply = async () => {
    if (!selected) return;
    const r = await fetch(`${API}/profiles/${selected}/apply`, { method: "POST" });
    const d = await r.json();
    setStatus(d.ok ? `Applied: ${selected}` : "Error applying profile");
  };

  return (
    <div className="panel">
      <h3>Machine Profiles</h3>
      <select value={selected} onChange={(e) => setSelected(e.target.value)}
        style={{ width: "100%", background: "#0f172a", color: "#e5e7eb", border: "1px solid #334155", borderRadius: 8, padding: "8px" }}>
        <option value="">-- Select profile --</option>
        {Object.keys(profiles).map(name => <option key={name} value={name}>{name}</option>)}
      </select>
      <button style={{ marginTop: 8, width: "100%" }} onClick={apply}>Apply Profile</button>
      {status && <p style={{ fontSize: 12, color: "#86efac", marginTop: 6 }}>{status}</p>}
    </div>
  );
}
