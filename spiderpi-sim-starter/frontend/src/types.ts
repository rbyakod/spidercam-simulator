export type Vec3 = { x: number; y: number; z: number };
export type AnchorMap = Record<string, [number, number, number]>;
export type SpiderState = {
  mode: string;
  status: string;
  estop: boolean;
  position: Vec3;
  target: Vec3;
  speed: number;
  anchors: AnchorMap;
  bounds: { x: [number, number]; y: [number, number]; z: [number, number] };
  lengths: Record<string, number>;
  steps: Record<string, number>;
  spools: Record<string, number>;
  trail: Vec3[];
  path: { name: string | null; index: number; points: Vec3[] };
  updated_at: number;
};
