import { useState } from "react";
import { computeFrame, FrameParams } from "../lib/frameSizing";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const DEFAULTS: FrameParams = {
  width: 2.0, depth: 2.0, height: 1.5,
  spoolRadius: 0.011, stepsPerRev: 200, microsteps: 16,
  carriageMass: 0.40, payloadMass: 0.08,
};

export function FrameSizingPanel() {
  const [params, setParams] = useState<FrameParams>(DEFAULTS);
  const [saved, setSaved] = useState(false);
  const derived = computeFrame(params);

  const set = (k: keyof FrameParams, v: number) => {
    setParams(prev => ({ ...prev, [k]: v }));
    setSaved(false);
  };

  const apply = async () => {
    await fetch(`${API}/config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ config: derived.configPatch }),
    });
    setSaved(true);
  };

  return (
    <div className="panel">
      <h3>Frame Sizing</h3>
      {(["width","depth","height","spoolRadius","carriageMass","payloadMass"] as (keyof FrameParams)[]).map(k => (
        <div key={k} className="field" style={{ marginBottom: 8 }}>
          <label>{k}</label>
          <input type="number" step={0.001} value={params[k]}
            onChange={(e) => set(k, Number(e.target.value))}
          />
        </div>
      ))}
      <div style={{ marginTop: 12, fontSize: 13 }}>
        <div className="kv"><span>Center cable length</span><span>{derived.centerLength.toFixed(3)} m</span></div>
        <div className="kv"><span>Steps/meter</span><span>{Math.round(derived.stepsPerMeter)}</span></div>
        <div className="kv"><span>Center tension</span><span>{derived.centerTension.toFixed(2)} N</span></div>
        <div className="kv"><span>Max speed</span><span>{derived.recommendedMaxSpeed.toFixed(2)} m/s</span></div>
        <div className="kv"><span>Max accel</span><span>{derived.recommendedAccel.toFixed(2)} m/s²</span></div>
        <div className="kv"><span>Cable spec</span><span>{derived.cableSpec}</span></div>
      </div>
      <button style={{ marginTop: 12, width: "100%" }} onClick={apply}>
        {saved ? "✓ Applied" : "Apply to simulator"}
      </button>
      <details style={{ marginTop: 8 }}>
        <summary style={{ cursor: "pointer", fontSize: 12, color: "#94a3b8" }}>Config patch JSON</summary>
        <pre className="codebox">{JSON.stringify(derived.configPatch, null, 2)}</pre>
      </details>
    </div>
  );
}
