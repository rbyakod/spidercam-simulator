import { useEffect, useRef, useState } from "react";
import { SpiderState } from "../types";

export function TopMap({
  state,
  move,
}: {
  state: SpiderState | null;
  move: (x: number, y: number, z: number, speed?: number) => void;
}) {
  const width = 280;
  const height = 280;
  const svgRef = useRef<SVGSVGElement | null>(null);
  const dragRef = useRef<number | null>(null);
  const lastSentAtRef = useRef(0);
  const [dragTarget, setDragTarget] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => {
    if (dragRef.current === null) return;

    const handlePointerMove = (event: PointerEvent) => {
      if (!state || dragRef.current !== event.pointerId) return;
      const svg = svgRef.current;
      if (!svg) return;
      const rect = svg.getBoundingClientRect();
      const px = Math.min(width, Math.max(0, event.clientX - rect.left));
      const py = Math.min(height, Math.max(0, event.clientY - rect.top));
      const [xmin, xmax] = state.bounds.x;
      const [ymin, ymax] = state.bounds.y;
      const nextX = xmin + (px / width) * (xmax - xmin);
      const nextY = ymin + (py / height) * (ymax - ymin);

      setDragTarget({ x: nextX, y: nextY });
      if (event.timeStamp - lastSentAtRef.current >= 80) {
        move(nextX, nextY, state.position.z, 0.45);
        lastSentAtRef.current = event.timeStamp;
      }
    };

    const handlePointerUp = (event: PointerEvent) => {
      if (!state || dragRef.current !== event.pointerId) return;
      if (dragTarget) {
        move(dragTarget.x, dragTarget.y, state.position.z, 0.45);
      }
      dragRef.current = null;
      lastSentAtRef.current = 0;
      setDragTarget(null);
    };

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);
    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    };
  }, [dragTarget, move, state]);

  if (!state) return <div className="panel">Loading map...</div>;

  const [xmin, xmax] = state.bounds.x;
  const [ymin, ymax] = state.bounds.y;
  const xToPx = (x: number) => ((x - xmin) / (xmax - xmin)) * width;
  const yToPx = (y: number) => ((y - ymin) / (ymax - ymin)) * height;
  const marker = dragTarget ?? { x: state.position.x, y: state.position.y };

  const handleMarkerPointerDown = (event: React.PointerEvent<SVGGElement>) => {
    if (state.estop) return;
    event.preventDefault();
    dragRef.current = event.pointerId;
    lastSentAtRef.current = event.timeStamp;
    setDragTarget({ x: state.position.x, y: state.position.y });
  };

  return (
    <div className="panel">
      <h3>XY Map</h3>
      <div className="mapHint">
        {state.estop ? "Reset E-Stop to enable drag moves" : "Drag the camera marker to move in X/Y"}
      </div>
      <svg ref={svgRef} width={width} height={height} className="map" viewBox={`0 0 ${width} ${height}`}>
        <rect x="0" y="0" width={width} height={height} fill="#121826" rx="10" />
        <rect x="18" y="18" width={width - 36} height={height - 36} rx="8" fill="none" stroke="#334155" strokeWidth="1.5" />
        {dragTarget ? (
          <circle
            cx={xToPx(state.position.x)}
            cy={yToPx(state.position.y)}
            r="7"
            fill="none"
            stroke="#f8fafc"
            strokeOpacity="0.55"
            strokeDasharray="4 4"
          />
        ) : null}
        <g
          className={`mapMarker ${state.estop ? "disabled" : ""}`}
          onPointerDown={handleMarkerPointerDown}
          role="button"
          aria-label="Drag camera in XY map"
        >
          <circle cx={xToPx(marker.x)} cy={yToPx(marker.y)} r="14" fill="transparent" />
          <circle cx={xToPx(marker.x)} cy={yToPx(marker.y)} r="8" fill="#f59e0b" />
          <circle cx={xToPx(marker.x)} cy={yToPx(marker.y)} r="3" fill="#fff7ed" />
        </g>
      </svg>
    </div>
  );
}
