import { SpiderState } from "../types";
import { SpoolWidget } from "./SpoolWidget";

export function PhysicsPanel({ state }: { state: SpiderState | null }) {
  if (!state?.physics) return <div className="panel"><h3>Motor Physics</h3><p>Loading physics...</p></div>;
  const p = state.physics;
  return (
    <div className="panel">
      <h3>Motor Physics</h3>
      <div className="kv"><span>Speed</span><span>{p.speed_mps.toFixed(3)} m/s</span></div>
      <div className="kv"><span>Current limit</span><span>{p.current_limit_a.toFixed(2)} A</span></div>
      <div className="kv"><span>Avail torque</span><span>{p.available_torque_nm.toFixed(3)} Nm</span></div>
      <div className="kv"><span>Hottest est</span><span>{p.hottest_temp_c.toFixed(1)} °C</span></div>
      <div className="kv"><span>Overload</span>
        <span className={p.overload ? "badTxt" : "okTxt"}>{p.overload ? "YES ⚠" : "No"}</span>
      </div>
      <div className="spoolGrid">
        {(["A","B","C","D"] as const).map((k) => {
          const m = p.motors?.[k];
          if (!m) return null;
          return (
            <SpoolWidget key={k} label={k}
              angle={state.spools?.[k] ?? 0}
              tension={m.tension_n}
              current={m.current_est_a}
              margin={m.margin}
              hot={m.temp_est_c > 75}
            />
          );
        })}
      </div>
    </div>
  );
}
