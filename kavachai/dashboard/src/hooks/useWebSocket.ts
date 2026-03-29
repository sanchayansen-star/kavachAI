"use client";
import { useEffect, useRef, useCallback, useState } from "react";
import type { DashboardEvent } from "@/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export function useWebSocket(onEvent?: (e: DashboardEvent) => void) {
  const ws = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);

  const connect = useCallback(() => {
    const socket = new WebSocket(`${WS_URL}/ws/dashboard?api_key=demo`);
    socket.onopen = () => setConnected(true);
    socket.onclose = () => {
      setConnected(false);
      setTimeout(connect, 3000);
    };
    socket.onmessage = (msg) => {
      try {
        const event = JSON.parse(msg.data) as DashboardEvent;
        onEvent?.(event);
      } catch {}
    };
    ws.current = socket;
  }, [onEvent]);

  useEffect(() => {
    connect();
    return () => ws.current?.close();
  }, [connect]);

  return { connected };
}
