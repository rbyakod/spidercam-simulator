import { useEffect, useRef, useState } from "react";
import { SpiderState } from "../types";
const WS_URL = "ws://127.0.0.1:8000/ws";
const HTTP_URL = "http://127.0.0.1:8000";
export function useSpiderSocket() {
  const [state, setState] = useState<SpiderState | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef<number | null>(null);
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
    fetch(`${HTTP_URL}/state`).then(r => r.json()).then(setState).catch(() => null);
    connect();
    return () => {
      if (retryRef.current) window.clearTimeout(retryRef.current);
      wsRef.current?.close();
    };
  }, []);
  const send = (msg: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) wsRef.current.send(JSON.stringify(msg));
  };
  return {
    state, connected,
    jog: (dx: number, dy: number, dz: number, speed = 0.4) => send({ type: "jog", dx, dy, dz, speed }),
    move: (x: number, y: number, z: number, speed = 0.4) => send({ type: "move", x, y, z, speed }),
    runPath: (name: string, opts: Record<string, number> = {}) => send({ type: "path", name, ...opts }),
    stop: () => send({ type: "stop" }),
    estop: () => send({ type: "estop" }),
    resetEstop: () => send({ type: "reset-estop" }),
  };
}
