import { SpiderState } from "../types";
export function Telemetry({ state, connected }:{ state: SpiderState | null; connected:boolean }) {
  if (!state) return <div className="panel">Loading state...</div>;
  return <div className="panel">
    <h3>Telemetry</h3>
    <div className="kv"><span>WS</span><span>{connected ? 'Connected' : 'Disconnected'}</span></div>
    <div className="kv"><span>Status</span><span>{state.status}</span></div>
    <div className="kv"><span>X</span><span>{state.position.x.toFixed(3)} m</span></div>
    <div className="kv"><span>Y</span><span>{state.position.y.toFixed(3)} m</span></div>
    <div className="kv"><span>Z</span><span>{state.position.z.toFixed(3)} m</span></div>
    <div className="kv"><span>Len A</span><span>{state.lengths.A?.toFixed(3)} m</span></div>
    <div className="kv"><span>Len B</span><span>{state.lengths.B?.toFixed(3)} m</span></div>
    <div className="kv"><span>Len C</span><span>{state.lengths.C?.toFixed(3)} m</span></div>
    <div className="kv"><span>Len D</span><span>{state.lengths.D?.toFixed(3)} m</span></div>
  </div>;
}
