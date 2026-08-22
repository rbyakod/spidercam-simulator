export interface Vec3 {
  x: number;
  y: number;
  z: number;
}

export interface TelemetryState {
  position: [number, number, number];
  target: [number, number, number];
  moving: boolean;
  cable_lengths: [number, number, number, number];
  e_stop: boolean;
  timestamp: number;
  faults: FaultEvent[];
  homing: HomingStatus;
  calibration: CalibrationStatus;
}

export interface FaultEvent {
  code: string;
  message: string;
  timestamp: number;
  axis: number | null;
}

export interface HomingStatus {
  homed: boolean[];
  all_homed: boolean;
  zero_offsets: number[];
}

export interface CalibrationStatus {
  step: string;
  step_index: number;
  total_steps: number;
  message: string;
  offsets: number[];
  is_calibrated: boolean;
}

export interface MotionProfile {
  name: string;
  max_speed: number;
  max_accel: number;
  jerk_limit: number | null;
  description: string;
}

export interface FrameDimensions {
  width: number;
  height: number;
  depth: number;
}
