import { SpiderState } from "../types";
export function Telemetry({ state, connected }:{ state: SpiderState | null; connected:boolean }) {
  if (!state) return <div className="panel">Loading state...</div>;
  return <div className="panel">
    <h3>Telemetry</h3>
    <div className="kv"><span>WS</span><span>{connected ? 'Connected' : 'Disconnected'}</span></div>
    <div className="kv"><span>Mode</span><span>{state.mode}</span></div>
    <div className="kv"><span>Status</span><span>{state.status}</span></div>
    <div className="kv"><span>Controller</span><span>{state.controller_ready ? 'Ready' : 'Not Ready'}</span></div>
    <div className="kv"><span>Armed</span><span>{state.armed ? 'Yes' : 'No'}</span></div>
    <div className="kv"><span>Geometry</span><span>{state.geometry_valid ? 'Valid' : 'Invalid'}</span></div>
    <div className="kv"><span>Calibration</span><span>{state.calibration_valid ? 'Valid' : 'Pending'}</span></div>
    <div className="kv"><span>X</span><span>{state.position.x.toFixed(3)} m</span></div>
    <div className="kv"><span>Y</span><span>{state.position.y.toFixed(3)} m</span></div>
    <div className="kv"><span>Z</span><span>{state.position.z.toFixed(3)} m</span></div>
    <div className="kv"><span>Len A</span><span>{state.lengths.A?.toFixed(3)} m</span></div>
    <div className="kv"><span>Len B</span><span>{state.lengths.B?.toFixed(3)} m</span></div>
    <div className="kv"><span>Len C</span><span>{state.lengths.C?.toFixed(3)} m</span></div>
    <div className="kv"><span>Len D</span><span>{state.lengths.D?.toFixed(3)} m</span></div>
    <div className="kv"><span>Faults</span><span>{state.faults.length ? state.faults.join(", ") : "None"}</span></div>
    <div className="kv"><span>Warnings</span><span>{state.warnings.length ? state.warnings.join(", ") : "None"}</span></div>
  </div>;
}
