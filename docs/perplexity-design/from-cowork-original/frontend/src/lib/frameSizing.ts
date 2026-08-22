export interface FrameParams {
  width: number;   // X span in meters
  depth: number;   // Y span in meters
  height: number;  // Z anchor height in meters
  spoolRadius: number;
  stepsPerRev: number;
  microsteps: number;
  carriageMass: number;
  payloadMass: number;
}

export interface FrameDerived {
  anchors: Record<string, [number, number, number]>;
  bounds: { x: [number, number]; y: [number, number]; z: [number, number] };
  centerLength: number;
  stepsPerMeter: number;
  centerTension: number;
  recommendedMaxSpeed: number;
  recommendedAccel: number;
  cableSpec: string;
  configPatch: object;
}

export function computeFrame(p: FrameParams): FrameDerived {
  const W = p.width, D = p.depth, H = p.height;
  const margin = 0.2;
  const anchors = {
    A: [0, 0, H] as [number, number, number],
    B: [W, 0, H] as [number, number, number],
    C: [W, D, H] as [number, number, number],
    D: [0, D, H] as [number, number, number],
  };
  const cx = W / 2, cy = D / 2, cz = H * 0.6;
  const centerLength = Math.sqrt(cx * cx + cy * cy + (H - cz) ** 2);
  const stepsPerMeter = (p.stepsPerRev * p.microsteps) / (2 * Math.PI * p.spoolRadius);
  const totalMass = p.carriageMass + p.payloadMass;
  const centerTension = (totalMass * 9.81) / 4;
  const recommendedMaxSpeed = Math.min(0.7, W * 0.35);
  const recommendedAccel = Math.min(0.9, W * 0.45);
  const cableSpec = p.spoolRadius < 0.012 ? "0.8mm Dyneema braid" : "1.0mm Dyneema braid";
  const configPatch = {
    frame: {
      anchors,
      bounds: {
        x: [margin, W - margin],
        y: [margin, D - margin],
        z: [H * 0.25, H * 0.85],
      },
      spool_radius_m: p.spoolRadius,
      motor_steps_per_rev: p.stepsPerRev,
    },
    rig: {
      carriage_mass_kg: p.carriageMass,
      payload_mass_kg: p.payloadMass,
      max_speed_mps: recommendedMaxSpeed,
      max_accel_mps2: recommendedAccel,
    },
  };
  return {
    anchors,
    bounds: {
      x: [margin, W - margin],
      y: [margin, D - margin],
      z: [H * 0.25, H * 0.85],
    },
    centerLength,
    stepsPerMeter,
    centerTension,
    recommendedMaxSpeed,
    recommendedAccel,
    cableSpec,
    configPatch,
  };
}
