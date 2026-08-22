import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export function HomingPanel() {
  const [switches, setSwitches] = useState<Record<string, boolean>>({});
  const [faults, setFaults] = useState<any>(null);
  const [paths, setPaths] = useState<{ paths: any; poses: any }>({ paths: {}, poses: {} });
  const [saveName, setSaveName] = useState("my_path");

  const load = async () => {
    const [s, f, p] = await Promise.all([
      fetch(`${API}/switches`).then(r => r.json()),
      fetch(`${API}/faults`).then(r => r.json()),
      fetch(`${API}/paths`).then(r => r.json()),
    ]);
    setSwitches(s); setFaults(f); setPaths(p);
  };

  useEffect(() => { load(); const id = setInterval(load, 800); return () => clearInterval(id); }, []);

  const post = async (path: string, body?: object, method = "POST") => {
    await fetch(`${API}${path}`, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    await load();
  };

  return (
    <div className="panel">
      <h3>Homing and Safety</h3>
      <div className="grid2">
        {["A","B","C","D"].map(axis => (
          <div key={axis} className="axisCard">
            <strong>Axis {axis}</strong>
            <span className={switches[axis] ? "badTxt" : "okTxt"} style={{ marginLeft: 8 }}>
              {switches[axis] ? "LIMIT" : "clear"}
            </span>
            <div className="inlineBtns" style={{ marginTop: 6 }}>
              <button onClick={() => post(`/wizard/homed`, { axis, homed: true })}>Mark homed</button>
            </div>
          </div>
        ))}
      </div>
      <div className="grid2" style={{ marginTop: 12 }}>
        <button onClick={() => post("/home/run", { axes: ["A","B","C","D"] })}>Home All</button>
        <button onClick={() => post("/faults/reset")}>Reset faults</button>
      </div>
      <div style={{ marginTop: 12, padding: 8, background: "#0b1020", borderRadius: 8 }}>
        <strong>Current fault: </strong>
        <span className={faults?.current?.active ? "badTxt" : "okTxt"}>
          {faults?.current?.active ? faults.current.code : "none"}
        </span>
        {faults?.current?.message && <p style={{ fontSize: 12, color: "#94a3b8", margin: "4px 0 0" }}>{faults.current.message}</p>}
      </div>
      <div style={{ marginTop: 16 }}>
        <h4 style={{ margin: "0 0 8px" }}>Record / Replay</h4>
        <div className="grid2">
          <button onClick={() => post("/record/start")}>Start record</button>
          <button onClick={() => post("/record/stop")}>Stop record</button>
        </div>
        <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
          <input value={saveName} onChange={(e) => setSaveName(e.target.value)}
            style={{ flex: 1, background: "#0f172a", color: "#e5e7eb", border: "1px solid #334155", borderRadius: 8, padding: "6px 10px" }}
            placeholder="Path name"
          />
          <button onClick={async () => {
            const s = await fetch(`${API}/state`).then(r => r.json());
            await post("/record/save", { name: saveName, points: s.recording.points, speed: s.speed });
          }}>Save</button>
        </div>
        <div className="pathList">
          {Object.keys(paths.paths || {}).map(name => (
            <div key={name} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "4px 0", borderBottom: "1px solid #1e293b" }}>
              <span>{name}</span>
              <div className="inlineBtns">
                <button onClick={() => post(`/paths/replay/${name}`)}>Replay</button>
                <button className="danger" onClick={() => post(`/paths/${name}`, undefined, "DELETE")}>Del</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
