import { SpiderState } from "../types";

export function Controls({
  state,
  jog,
  runPath,
  setMode,
  arm,
  disarm,
  home,
  verifyLimits,
  verifyMotorDirections,
  calibrate,
  stop,
  estop,
  resetEstop,
}: {
  state: SpiderState | null;
  jog: (dx: number, dy: number, dz: number, speed?: number) => void;
  runPath: (name: string, opts?: Record<string, number>) => void;
  setMode: (mode: "sim" | "dry_run" | "hardware") => void;
  arm: () => void;
  disarm: () => void;
  home: () => void;
  verifyLimits: () => void;
  verifyMotorDirections: () => void;
  calibrate: () => void;
  stop: () => void;
  estop: () => void;
  resetEstop: () => void;
}) {
  if (!state) return <div className="panel">Loading controls...</div>;

  return (
    <div className="panel">
      <h3>Controls</h3>
      <div className="mapHint">
        Mode: {state.mode} | Status: {state.status}
      </div>
      <div className="grid3">
        <button type="button" onClick={() => setMode("sim")}>Sim</button>
        <button type="button" onClick={() => setMode("dry_run")}>Dry Run</button>
        <button type="button" onClick={() => setMode("hardware")}>Hardware</button>
      </div>
      <div className="grid2" style={{ marginTop: 12 }}>
        <button type="button" onClick={arm}>Arm</button>
        <button type="button" onClick={disarm}>Disarm</button>
      </div>
      <div className="grid2" style={{ marginTop: 12 }}>
        <button type="button" onClick={home}>Home</button>
        <button type="button" onClick={calibrate}>Calibrate</button>
      </div>
      <div className="grid2" style={{ marginTop: 12 }}>
        <button type="button" onClick={verifyLimits}>Verify Limits</button>
        <button type="button" onClick={verifyMotorDirections}>Verify Directions</button>
      </div>
      <div className="grid2" style={{ marginTop: 12 }}>
        <button type="button" onClick={() => jog(0, -0.1, 0)}>Forward</button>
        <button type="button" onClick={() => jog(0, 0.1, 0)}>Back</button>
        <button type="button" onClick={() => jog(-0.1, 0, 0)}>Left</button>
        <button type="button" onClick={() => jog(0.1, 0, 0)}>Right</button>
        <button type="button" onClick={() => jog(0, 0, -0.08)}>Down</button>
        <button type="button" onClick={() => jog(0, 0, 0.08)}>Up</button>
      </div>
      <div className="grid2" style={{ marginTop: 12 }}>
        <button type="button" onClick={() => runPath("square", { size: 0.8, z: state.target.z, speed: 0.35 })}>Square</button>
        <button type="button" onClick={() => runPath("circle", { radius: 0.45, z: state.target.z, speed: 0.35 })}>Circle</button>
      </div>
      <div className="grid2" style={{ marginTop: 12 }}>
        <button type="button" onClick={stop}>Stop</button>
        <button type="button" className="danger" onClick={estop}>E-STOP</button>
      </div>
      <button type="button" className="warn" onClick={resetEstop} style={{ marginTop: 12 }}>Reset E-Stop</button>
    </div>
  );
}
