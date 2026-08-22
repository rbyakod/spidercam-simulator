import { SpiderState } from "../types";
import { Joystick } from "./Joystick";

export function Controls({ state, jog, move, preset, runPath, home, stop, estop, resetEstop }:
  { state: SpiderState | null; jog: (dx: number, dy: number, dz: number, speed?: number) => void;
    move: (x: number, y: number, z: number, speed?: number) => void;
    preset: (name: string, speed?: number) => void;
    runPath: (name: string, opts?: Record<string, unknown>) => void;
    home: () => void; stop: () => void; estop: () => void; resetEstop: () => void; }) {
  if (!state) return <div className="panel"><h3>Controls</h3><p>Loading controls...</p></div>;
  const z = state.target.z;
  let timer: number | null = null;
  const joystickMove = (nx: number, ny: number) => {
    if (timer) window.clearInterval(timer);
    timer = window.setInterval(() => { jog(nx * 0.03, ny * 0.03, 0, 0.35); }, 80);
  };
  const joystickEnd = () => { if (timer) window.clearInterval(timer); stop(); };
  return (
    <div className="panel">
      <h3>Controls</h3>
      <Joystick onMove={joystickMove} onEnd={joystickEnd} />
      <div className="grid2">
        <button onClick={() => jog(0,-0.10,0)}>Forward</button>
        <button onClick={() => jog(0,0.10,0)}>Back</button>
        <button onClick={() => jog(-0.10,0,0)}>Left</button>
        <button onClick={() => jog(0.10,0,0)}>Right</button>
        <button onClick={() => jog(0,0,0.08)}>Down</button>
        <button onClick={() => jog(0,0,-0.08)}>Up</button>
      </div>
      <div className="sliderLabel">
        <span>Z target: {z.toFixed(2)} m</span>
        <input type="range" min={0.3} max={1.3} step={0.01} value={z}
          onChange={(e) => move(state.target.x, state.target.y, Number(e.target.value))} />
      </div>
      <div className="grid2" style={{marginTop:8}}>
        <button onClick={() => preset("center")}>Center</button>
        <button onClick={() => preset("low_center")}>Low center</button>
        <button onClick={() => preset("front_left")}>Front-left</button>
        <button onClick={() => preset("front_right")}>Front-right</button>
        <button onClick={() => preset("rear_left")}>Rear-left</button>
        <button onClick={() => preset("rear_right")}>Rear-right</button>
      </div>
      <div className="grid2" style={{marginTop:8}}>
        <button onClick={() => runPath("square",{size:0.8,z,speed:0.35})}>Square path</button>
        <button onClick={() => runPath("circle",{radius:0.45,z,speed:0.35})}>Circle path</button>
        <button onClick={() => runPath("diagonal",{z,speed:0.35})}>Diagonal</button>
        <button onClick={stop}>Stop path</button>
      </div>
      <div className="grid2" style={{marginTop:8}}>
        <button onClick={home}>Home</button>
        <button onClick={stop}>Stop</button>
      </div>
      <div className="grid2" style={{marginTop:8}}>
        <button className="danger" onClick={estop}>E-STOP</button>
        <button className="warn" onClick={resetEstop}>Reset E-Stop</button>
      </div>
    </div>
  );
}
