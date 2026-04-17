import { useSpiderSocket } from "./hooks/useSpiderSocket";
import { SpiderScene } from "./components/SpiderScene";
import { Controls } from "./components/Controls";
import { Telemetry } from "./components/Telemetry";
import { TopMap } from "./components/TopMap";

export default function App() {
  const { state, connected, jog, runPath, stop, estop, resetEstop } = useSpiderSocket();
  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>SpiderPi Simulator</h1>
          <p>MacBook starter project for React + Three.js + FastAPI</p>
        </div>
        <div className={`pill ${connected ? "ok" : "bad"}`}>{connected ? "WS Connected" : "WS Disconnected"}</div>
      </header>
      <main className="layout">
        <section className="left"><SpiderScene state={state} /></section>
        <section className="right">
          <Controls state={state} jog={jog} runPath={runPath} stop={stop} estop={estop} resetEstop={resetEstop} />
          <TopMap state={state} />
          <Telemetry state={state} connected={connected} />
        </section>
      </main>
    </div>
  );
}
