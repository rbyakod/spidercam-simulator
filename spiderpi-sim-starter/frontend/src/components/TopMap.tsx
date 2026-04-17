import { SpiderState } from "../types";
export function TopMap({ state }:{ state: SpiderState | null }) {
  if (!state) return <div className="panel">Loading map...</div>;
  const width = 280, height = 280;
  const [xmin, xmax] = state.bounds.x;
  const [ymin, ymax] = state.bounds.y;
  const xToPx = (x:number) => ((x-xmin)/(xmax-xmin))*width;
  const yToPx = (y:number) => ((y-ymin)/(ymax-ymin))*height;
  return <div className="panel"><h3>XY Map</h3><svg width={width} height={height} className="map"><rect x="0" y="0" width={width} height={height} fill="#121826" rx="10" /><circle cx={xToPx(state.position.x)} cy={yToPx(state.position.y)} r="8" fill="#f59e0b" /></svg></div>;
}
