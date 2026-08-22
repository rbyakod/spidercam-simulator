import { useSpiderSocket } from "./hooks/useSpiderSocket";
import { SpiderScene } from "./components/SpiderScene";
import { Controls } from "./components/Controls";
import { Telemetry } from "./components/Telemetry";
import { TopMap } from "./components/TopMap";
import { PhysicsPanel } from "./components/PhysicsPanel";
import { CalibrationPanel } from "./components/CalibrationPanel";
import { HomingPanel } from "./components/HomingPanel";
import { FrameSizingPanel } from "./components/FrameSizingPanel";
import { ProfileSelector } from "./components/ProfileSelector";
import { ProfileManager } from "./components/ProfileManager";
import { CalibrationWizard } from "./components/CalibrationWizard";
import { HardwareGatePanel } from "./components/HardwareGatePanel";

export default function App() {
  const { state, connected, jog, move, preset, runPath, home, stop, estop, resetEstop } =
    useSpiderSocket();

  return (
    <div className="app">
      <div className="topbar">
        <div>
          <h1>SpiderPi Simulator</h1>
          <p>3D rig · Path planner · Joystick · Motor-load simulation</p>
        </div>
        <span className={`pill ${connected ? "ok" : "bad"}`}>
          {connected ? "WS Connected" : "WS Disconnected"}
        </span>
      </div>
      <div className="layout">
        <div className="left">
          <div className="sceneWrap">
            <SpiderScene state={state} />
          </div>
        </div>
        <div className="right">
          <Telemetry state={state} connected={connected} />
          <Controls state={state} jog={jog} move={move} preset={preset}
            runPath={runPath} home={home} stop={stop} estop={estop} resetEstop={resetEstop} />
          <TopMap state={state} onMove={(x, y) => {
            if (!state) return;
            move(x, y, state.target.z, state.speed);
          }} />
          <PhysicsPanel state={state} />
          <FrameSizingPanel />
          <ProfileSelector />
          <ProfileManager />
          <CalibrationWizard />
          <CalibrationPanel />
          <HomingPanel />
          <HardwareGatePanel />
        </div>
      </div>
    </div>
  );
}
