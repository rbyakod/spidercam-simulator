import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export function CalibrationWizard() {
  const [steps, setSteps] = useState<any[]>([]);
  const [focused, setFocused] = useState<string | null>(null);

  const load = async () => {
    const r = await fetch(`${API}/wizard/checklist`);
    setSteps(await r.json());
  };

  useEffect(() => { load(); }, []);

  const markStep = async (step_id: string, done: boolean) => {
    await fetch(`${API}/wizard/step`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ step_id, done, notes: "" }),
    });
    await load();
  };

  const reset = async () => {
    await fetch(`${API}/wizard/reset`, { method: "POST" });
    await load();
  };

  return (
    <div className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ margin: 0 }}>Calibration Wizard</h3>
        <button className="warn" onClick={reset} style={{ fontSize: 11, padding: "4px 8px" }}>Reset</button>
      </div>
      {steps.map(s => (
        <div key={s.id} className="wizardStep" style={{ marginTop: 10, opacity: s.done ? 0.6 : 1 }}>
          <div className="wizardHead">
            <strong>{s.title}</strong>
            <span className={s.done ? "okTxt" : "warnTxt"}>{s.done ? "✓ Done" : "Pending"}</span>
          </div>
          {focused === s.id && (
            <ul style={{ fontSize: 12, color: "#94a3b8", margin: "4px 0 8px", paddingLeft: 16 }}>
              {s.tasks.map((t: string, i: number) => <li key={i}>{t}</li>)}
            </ul>
          )}
          <div style={{ display: "flex", gap: 8 }}>
            <button style={{ fontSize: 11, padding: "3px 8px" }}
              onClick={() => setFocused(focused === s.id ? null : s.id)}>
              {focused === s.id ? "Hide" : "Show tasks"}
            </button>
            <button style={{ fontSize: 11, padding: "3px 8px" }} className={s.done ? "warn" : ""}
              onClick={() => markStep(s.id, !s.done)}>
              {s.done ? "Mark pending" : "Mark done"}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
