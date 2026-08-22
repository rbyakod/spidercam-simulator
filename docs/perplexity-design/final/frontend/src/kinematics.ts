import { Vec3, FrameDimensions } from './types';

export function getAnchors(frame: FrameDimensions): Vec3[] {
  return [
    { x: 0,           y: frame.height, z: 0           },
    { x: frame.width, y: frame.height, z: 0           },
    { x: 0,           y: frame.height, z: frame.depth },
    { x: frame.width, y: frame.height, z: frame.depth },
  ];
}

export function cableLengths(pos: Vec3, frame: FrameDimensions): number[] {
  const anchors = getAnchors(frame);
  return anchors.map(a => Math.sqrt(
    Math.pow(a.x - pos.x, 2) +
    Math.pow(a.y - pos.y, 2) +
    Math.pow(a.z - pos.z, 2)
  ));
}

export function clampToWorkspace(pos: Vec3, frame: FrameDimensions, margin = 0.05): Vec3 {
  return {
    x: Math.max(margin, Math.min(frame.width  - margin, pos.x)),
    y: Math.max(margin, Math.min(frame.height - margin, pos.y)),
    z: Math.max(margin, Math.min(frame.depth  - margin, pos.z)),
  };
}
