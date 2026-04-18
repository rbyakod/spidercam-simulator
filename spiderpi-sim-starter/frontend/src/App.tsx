import { useEffect, useRef, useState } from "react";
import { useSpiderSocket } from "./hooks/useSpiderSocket";
import { SpiderScene } from "./components/SpiderScene";
import { Controls } from "./components/Controls";
import { Telemetry } from "./components/Telemetry";
import { TopMap } from "./components/TopMap";
import { FramePlanner } from "./components/FramePlanner";

export default function App() {
  const [activeTab, setActiveTab] = useState<"simulator" | "planner">("simulator");
  const [sceneMode, setSceneMode] = useState<"engineering" | "stadium">("engineering");
  const [lightingMode, setLightingMode] = useState<"day" | "night">("day");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState(420);
  const [isResizing, setIsResizing] = useState(false);
  const layoutRef = useRef<HTMLElement | null>(null);
  const { state, connected, jog, move, runPath, stop, estop, resetEstop } = useSpiderSocket();

  useEffect(() => {
    if (!isResizing) return;

    const updateWidth = (clientX: number) => {
      const layout = layoutRef.current;
      if (!layout) return;
      const rect = layout.getBoundingClientRect();
      const minWidth = 280;
      const maxWidth = Math.min(720, Math.max(minWidth, rect.width - 360));
      const nextWidth = rect.right - clientX;
      const clampedWidth = Math.min(maxWidth, Math.max(minWidth, nextWidth));
      setSidebarWidth(clampedWidth);
    };

    const handlePointerMove = (event: PointerEvent) => updateWidth(event.clientX);
    const handlePointerUp = () => setIsResizing(false);

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";

    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
  }, [isResizing]);

  const handleResizeStart = (event: React.PointerEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (sidebarCollapsed) return;
    setIsResizing(true);
  };

  const layoutStyle = {
    ["--sidebar-width" as const]: `${sidebarWidth}px`,
  } as React.CSSProperties;

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>SpiderPi Simulator</h1>
          <p>MacBook starter project for React + Three.js + FastAPI</p>
        </div>
        <div className="statusCluster">
          <div className="viewToggle" aria-label="Application tab">
            <button
              className={activeTab === "simulator" ? "active" : ""}
              onClick={() => setActiveTab("simulator")}
              type="button"
            >
              Simulator
            </button>
            <button
              className={activeTab === "planner" ? "active" : ""}
              onClick={() => setActiveTab("planner")}
              type="button"
            >
              Frame Planner
            </button>
          </div>
          <div className="viewToggle" aria-label="Scene mode">
            <button
              className={sceneMode === "engineering" ? "active" : ""}
              onClick={() => setSceneMode("engineering")}
              type="button"
            >
              Engineering
            </button>
            <button
              className={sceneMode === "stadium" ? "active" : ""}
              onClick={() => setSceneMode("stadium")}
              type="button"
            >
              Stadium
            </button>
          </div>
          <button
            className="sidebarToggle"
            onClick={() => setSidebarCollapsed((value) => !value)}
            type="button"
          >
            {sidebarCollapsed ? "Show Sidebar" : "Hide Sidebar"}
          </button>
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
      <main
        ref={layoutRef}
        className={`layout ${activeTab === "planner" ? "layoutPlanner" : ""} ${sidebarCollapsed ? "layoutExpanded" : ""} ${isResizing ? "layoutResizing" : ""}`}
        style={layoutStyle}
      >
        {activeTab === "simulator" ? (
          <>
            <section className="left">
              <SpiderScene state={state} lightingMode={lightingMode} sceneMode={sceneMode} />
            </section>
            <section className={`right ${sidebarCollapsed ? "rightCollapsed" : ""}`}>
              <div
                className="columnResizer"
                onPointerDown={handleResizeStart}
                role="separator"
                aria-orientation="vertical"
                aria-label="Resize sidebar"
              />
              <Controls state={state} jog={jog} runPath={runPath} stop={stop} estop={estop} resetEstop={resetEstop} />
              <TopMap state={state} move={move} />
              <Telemetry state={state} connected={connected} />
            </section>
          </>
        ) : (
          <section className="plannerShell">
            <FramePlanner state={state} />
          </section>
        )}
      </main>
    </div>
  );
}
