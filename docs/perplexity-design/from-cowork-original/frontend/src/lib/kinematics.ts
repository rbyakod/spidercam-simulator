import { AnchorMap, Vec3 } from "../types";

export function lengthsFromXYZ(anchors: AnchorMap, p: Vec3) {
  const out: Record<string, number> = {};
  for (const [k, [ax, ay, az]] of Object.entries(anchors)) {
    out[k] = Math.sqrt((p.x - ax) ** 2 + (p.y - ay) ** 2 + (p.z - az) ** 2);
  }
  return out;
}

export function fmt(n: number, digits = 3) {
  return n.toFixed(digits);
}
