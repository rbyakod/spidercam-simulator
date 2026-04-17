import { useState } from "react";
import { useSpiderSocket } from "./hooks/useSpiderSocket";
import { SpiderScene } from "./components/SpiderScene";
import { Controls } from "./components/Controls";
import { Telemetry } from "./components/Telemetry";
import { TopMap } from "./components/TopMap";

export default function App() {
  const [lightingMode, setLightingMode] = useState<"day" | "night">("day");
  const { state, connected, jog, runPath, stop, estop, resetEstop } = useSpiderSocket();
  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>SpiderPi Simulator</h1>
          <p>MacBook starter project for React + Three.js + FastAPI</p>
        </div>
        <div className="statusCluster">
          <div className="viewToggle" aria-label="Stadium lighting">
            <button
              className={lightingMode === "day" ? "active" : ""}
              onClick={() => setLightingMode("day")}
              type="button"
            >
              Day Broadcast
            </button>
            <button
              className={lightingMode === "night" ? "active" : ""}
              onClick={() => setLightingMode("night")}
              type="button"
            >
              Night Match
            </button>
          </div>
          <div className={`pill ${connected ? "ok" : "bad"}`}>{connected ? "WS Connected" : "WS Disconnected"}</div>
        </div>
      </header>
      <main className="layout">
        <section className="left"><SpiderScene state={state} lightingMode={lightingMode} /></section>
        <section className="right">
          <Controls state={state} jog={jog} runPath={runPath} stop={stop} estop={estop} resetEstop={resetEstop} />
          <TopMap state={state} />
          <Telemetry state={state} connected={connected} />
        </section>
      </main>
    </div>
  );
}
