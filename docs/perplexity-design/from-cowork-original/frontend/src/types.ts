export type Vec3 = { x: number; y: number; z: number };
export type AnchorMap = Record<string, [number, number, number]>;

export type MotorPhysics = {
  tension_n: number;
  torque_need_nm: number;
  torque_avail_nm: number;
  current_est_a: number;
  current_limit_a: number;
  margin: number;
  temp_est_c: number;
  line_pull_capacity_n: number;
};

export type SpiderState = {
  mode: "sim" | "live";
  status: string;
  fault: string | null;
  estop: boolean;
  position: Vec3;
  target: Vec3;
  velocity: Vec3;
  accel: Vec3;
  speed: number;
  anchors: AnchorMap;
  bounds: { x: [number, number]; y: [number, number]; z: [number, number] };
  lengths: Record<string, number>;
  steps: Record<string, number>;
  spools: Record<string, number>;
  trail: Vec3[];
  path: { name: string | null; index: number; points: Vec3[] };
  presets: Record<string, Vec3>;
  physics: {
    speed_mps: number;
    current_limit_a: number;
    available_torque_nm: number;
    overload: boolean;
    hottest_temp_c: number;
    motors: Record<string, MotorPhysics>;
  };
  fault_info: { active: boolean; code: string | null; message: string | null };
  limit_switches: Record<string, boolean>;
  recording: { active: boolean; points: Vec3[]; started_at: number | null };
  saved_paths: Record<string, any>;
  saved_poses: Record<string, Vec3>;
  updated_at: number;
};
