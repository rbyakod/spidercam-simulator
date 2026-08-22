import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export function ProfileManager() {
  const [profiles, setProfiles] = useState<Record<string, any>>({});
  const [newName, setNewName] = useState("my_profile");
  const [exported, setExported] = useState("");
  const [status, setStatus] = useState("");

  const load = async () => {
    const r = await fetch(`${API}/profiles`);
    const d = await r.json();
    setProfiles(d.profiles || {});
  };

  useEffect(() => { load(); }, []);

  const saveCurrent = async () => {
    await fetch(`${API}/profiles/save-current`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName }),
    });
    setStatus(`Saved as "${newName}"`);
    await load();
  };

  const exportYaml = async () => {
    const r = await fetch(`${API}/config`);
    const d = await r.json();
    setExported(JSON.stringify(d, null, 2));
  };

  return (
    <div className="panel">
      <h3>Profile Manager</h3>
      <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
        <input value={newName} onChange={(e) => setNewName(e.target.value)}
          style={{ flex: 1, background: "#0f172a", color: "#e5e7eb", border: "1px solid #334155", borderRadius: 8, padding: "6px 10px" }}
        />
        <button onClick={saveCurrent}>Save current</button>
      </div>
      {status && <p style={{ fontSize: 12, color: "#86efac" }}>{status}</p>}
      <button onClick={exportYaml} style={{ width: "100%", marginBottom: 8 }}>Export current config</button>
      {exported && (
        <pre className="codebox" style={{ maxHeight: 200 }}>{exported}</pre>
      )}
      <div style={{ marginTop: 12 }}>
        <strong>Saved profiles:</strong>
        {Object.keys(profiles).map(name => (
          <div key={name} style={{ padding: "4px 0", borderBottom: "1px solid #1e293b" }}>{name}</div>
        ))}
      </div>
    </div>
  );
}
