import { useEffect, useRef, useState, useCallback } from 'react';
import { TelemetryState } from './types';

const WS_URL = (import.meta as any).env?.VITE_WS_URL ?? 'ws://localhost:8000/ws/telemetry';
const RECONNECT_DELAY_MS = 2000;

export function useSpiderSocket() {
  const [telemetry, setTelemetry] = useState<TelemetryState | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  const connect = useCallback(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => {
      setConnected(false);
      timerRef.current = setTimeout(connect, RECONNECT_DELAY_MS);
    };
    ws.onerror = () => ws.close();
    ws.onmessage = (ev) => {
      try {
        setTelemetry(JSON.parse(ev.data) as TelemetryState);
      } catch {
        // ignore malformed messages
      }
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(timerRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { telemetry, connected };
}
