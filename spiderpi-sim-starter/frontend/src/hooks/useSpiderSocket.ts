import { useEffect, useRef, useState } from "react";
import { SpiderState } from "../types";

const WS_URL = "ws://127.0.0.1:8000/ws";
const HTTP_URL = "http://127.0.0.1:8000";

export function useSpiderSocket() {
  const [state, setState] = useState<SpiderState | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef<number | null>(null);
  const pollRef = useRef<number | null>(null);

  const refreshState = () => {
    fetch(`${HTTP_URL}/state`)
      .then((response) => response.json())
      .then(setState)
      .catch(() => null);
  };

  const connect = () => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.type === "state") setState(msg);
    };
    ws.onclose = () => {
      setConnected(false);
      retryRef.current = window.setTimeout(connect, 1000);
    };
    ws.onerror = () => ws.close();
  };

  useEffect(() => {
    refreshState();
    connect();
    pollRef.current = window.setInterval(refreshState, 250);
    return () => {
      if (retryRef.current) window.clearTimeout(retryRef.current);
      if (pollRef.current) window.clearInterval(pollRef.current);
      wsRef.current?.close();
    };
  }, []);

  const post = async (path: string, payload?: object) => {
    await fetch(`${HTTP_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload ? JSON.stringify(payload) : undefined,
    }).catch(() => null);
    refreshState();
  };

  const jog = (dx: number, dy: number, dz: number, speed = 0.4) => {
    if (!state) return;
    void post("/move", {
      x: state.position.x + dx,
      y: state.position.y + dy,
      z: state.position.z + dz,
      speed,
    });
  };

  const move = (x: number, y: number, z: number, speed = 0.4) => {
    void post("/move", { x, y, z, speed });
  };

  const runPath = (name: string, opts: Record<string, number> = {}) => {
    void post("/path", { name, ...opts });
  };

  return {
    state,
    connected,
    jog,
    move,
    runPath,
    stop: () => void post("/stop"),
    estop: () => void post("/estop"),
    resetEstop: () => void post("/reset-estop"),
  };
}
