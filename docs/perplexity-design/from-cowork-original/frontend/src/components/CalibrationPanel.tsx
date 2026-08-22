import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export function CalibrationPanel() {
  const [wizard, setWizard] = useState<any>(null);
  const [radius, setRadius] = useState("0.011");

  const load = async () => {
    const r = await fetch(`${API}/wizard`);
    setWizard(await r.json());
  };

  useEffect(() => { load(); }, []);

  const post = async (path: string, body: object) => {
    await fetch(`${API}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    await load();
  };

  return (
    <div className="panel">
      <h3>Calibration Wizard</h3>
      {wizard?.steps?.map((s: any) => (
        <div key={s.step} style={{ marginBottom: 10, padding: 8, border: "1px solid #334155", borderRadius: 8 }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <strong>{s.step}</strong>
            <span className={s.done ? "okTxt" : "warnTxt"}>{s.done ? "Done" : "Pending"}</span>
          </div>
          <p style={{ fontSize: 12, color: "#94a3b8", margin: "4px 0 0" }}>{s.instructions}</p>
        </div>
      ))}
      <div className="grid2" style={{ marginTop: 12 }}>
        {["A","B","C","D"].map(axis => (
          <button key={axis} onClick={() => post("/wizard/motor-direction", { axis, invert_dir: false, ok: true })}>
            Dir OK: {axis}
          </button>
        ))}
        {["A","B","C","D"].map(axis => (
          <button key={"h"+axis} onClick={() => post("/wizard/homed", { axis, homed: true })}>
            Home OK: {axis}
          </button>
        ))}
      </div>
      <div className="sliderLabel" style={{ marginTop: 12 }}>
        <span>Spool radius (m)</span>
        <input type="number" step={0.001} min={0.005} max={0.05}
          value={radius} onChange={(e) => setRadius(e.target.value)}
          style={{ background: "#0f172a", color: "#e5e7eb", border: "1px solid #334155", borderRadius: 8, padding: "6px 10px" }}
        />
        <button onClick={() => post("/wizard/spool-radius", { radius_m: Number(radius) })}>
          Save spool radius
        </button>
      </div>
      <div className="grid2" style={{ marginTop: 8 }}>
        <button onClick={() => post("/wizard/zero-lengths", { lengths: { A: 1.2, B: 1.2, C: 1.2, D: 1.2 } })}>
          Save zero lengths
        </button>
        <button onClick={() => post("/wizard/bounds", { xmin:0.2,xmax:1.8,ymin:0.2,ymax:1.8,zmin:0.3,zmax:1.3 })}>
          Save bounds
        </button>
      </div>
    </div>
  );
}
