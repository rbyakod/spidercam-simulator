from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from math import sqrt, pi
from typing import Dict, Set, Optional
import asyncio, json, time

from persistent_config import load_config, save_config, SystemConfig
from calibration import (get_wizard_state, set_motor_direction, set_homed,
                         set_spool_radius, set_zero_lengths, set_line_offsets, set_bounds)
from calibration_state import get_wizard_with_checklist, mark_step, reset_wizard
from calibration_gates import compute_gates, step_gate_status
from physics import motor_metrics
from planner import square_path, circle_path, diagonal_sweep
from faults import FaultManager
from path_store import list_paths, upsert_path, delete_path, upsert_pose
from profile_store import load_profiles, save_profile, list_profiles, get_profile
from homing_monitor import HomingMonitor
from hardware_runtime import HardwareRuntime
from runtime_factory import build_backend
from hardware_executor import HardwareExecutor

app = FastAPI(title="SpiderPi Control API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cfg():
    return load_config()

def clamp(v, rng):
    return max(rng[0], min(rng[1], v))

def anchors():
    return cfg().frame.anchors

def bounds():
    return cfg().frame.bounds

def spool_radius():
    return cfg().frame.spool_radius_m

def steps_per_meter():
    c = cfg()
    return (c.frame.motor_steps_per_rev * c.motors.microsteps) / (2 * pi * c.frame.spool_radius_m)

def lengths_from_xyz(x: float, y: float, z: float) -> Dict[str, float]:
    out = {}
    for name, (ax, ay, az) in anchors().items():
        out[name] = sqrt((x-ax)**2 + (y-ay)**2 + (z-az)**2)
    return out

def steps_from_delta_length(delta_len: float) -> int:
    return int(delta_len * steps_per_meter())

def within_bounds(x: float, y: float, z: float):
    b = bounds()
    return b["x"][0] <= x <= b["x"][1] and b["y"][0] <= y <= b["y"][1] and b["z"][0] <= z <= b["z"][1]

class Target(BaseModel):
    x: float; y: float; z: float; speed: float = 0.4

class PathCmd(BaseModel):
    name: str; speed: float = 0.35; size: float = 0.8; radius: float = 0.45; z: float = 0.9

class DirectionCmd(BaseModel):
    axis: str; invert_dir: bool; ok: bool

class HomedCmd(BaseModel):
    axis: str; homed: bool

class SpoolRadiusCmd(BaseModel):
    radius_m: float

class ZeroLengthsCmd(BaseModel):
    lengths: Dict[str, float]

class LineOffsetsCmd(BaseModel):
    offsets: Dict[str, int]

class BoundsCmd(BaseModel):
    xmin: float; xmax: float; ymin: float; ymax: float; zmin: float; zmax: float

class ConfigUpdateCmd(BaseModel):
    config: dict

class PathSaveCmd(BaseModel):
    name: str; points: list[dict]; speed: float = 0.25

class PoseSaveCmd(BaseModel):
    name: str; x: float; y: float; z: float

class HomeCmd(BaseModel):
    axes: Optional[list[str]] = None

class ProfileSaveCmd(BaseModel):
    name: str

class WizardStepCmd(BaseModel):
    step_id: str; done: bool; notes: str = ""

class Manager:
    def __init__(self):
        self.clients: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.add(ws)

    def disconnect(self, ws: WebSocket):
        self.clients.discard(ws)

    async def broadcast(self, payload: dict):
        dead = []
        for client in list(self.clients):
            try:
                await client.send_text(json.dumps(payload))
            except Exception:
                dead.append(client)
        for d in dead:
            self.disconnect(d)

manager = Manager()
fault_mgr = FaultManager()
homing_monitor = HomingMonitor()
motion_backend = None
executor = None
hardware_rt = None

STATE = {
    "mode": "sim", "status": "idle", "fault": None, "estop": False,
    "position": {"x": 1.0, "y": 1.0, "z": 0.9},
    "target": {"x": 1.0, "y": 1.0, "z": 0.9},
    "velocity": {"x": 0.0, "y": 0.0, "z": 0.0},
    "accel": {"x": 0.0, "y": 0.0, "z": 0.0},
    "speed": 0.4,
    "anchors": {}, "bounds": {},
    "lengths": {}, "steps": {"A": 0, "B": 0, "C": 0, "D": 0},
    "spools": {"A": 0.0, "B": 0.0, "C": 0.0, "D": 0.0},
    "path": {"name": None, "index": 0, "points": []},
    "trail": [], "physics": {}, "wizard": {}, "fault_info": {},
    "limit_switches": {"A": False, "B": False, "C": False, "D": False},
    "recording": {"active": False, "points": [], "started_at": None},
    "saved_paths": {}, "saved_poses": {}, "updated_at": time.time(),
}

def refresh_from_config():
    c = cfg()
    STATE["anchors"] = c.frame.anchors
    STATE["bounds"] = c.frame.bounds
    STATE["wizard"] = get_wizard_state()

def refresh_saved_paths():
    paths, poses = list_paths()
    STATE["saved_paths"] = paths
    STATE["saved_poses"] = poses

def set_target(x, y, z, speed):
    b = bounds()
    x = clamp(x, b["x"]); y = clamp(y, b["y"]); z = clamp(z, b["z"])
    STATE["target"] = {"x": x, "y": y, "z": z}
    STATE["speed"] = max(0.05, min(speed, cfg().rig.max_speed_mps))
    STATE["status"] = "moving"

def set_path(name, points):
    STATE["path"] = {"name": name, "index": 0, "points": points}
    if points:
        p = points[0]
        set_target(p["x"], p["y"], p["z"], STATE["speed"])

def apply_position(x, y, z, dt):
    prev_pos = STATE["position"].copy()
    prev_vel = STATE["velocity"].copy()
    prev_lengths = STATE["lengths"].copy()
    next_lengths = lengths_from_xyz(x, y, z)
    step_delta = {}
    spool_delta = {}
    for k in next_lengths:
        dl = next_lengths[k] - prev_lengths.get(k, next_lengths[k])
        step_delta[k] = steps_from_delta_length(dl)
        spool_delta[k] = dl / max(spool_radius(), 1e-6)
    STATE["steps"] = {k: STATE["steps"][k] + step_delta.get(k, 0) for k in STATE["steps"]}
    STATE["spools"] = {k: STATE["spools"][k] + spool_delta.get(k, 0) for k in STATE["spools"]}
    vx = (x - prev_pos["x"]) / max(dt, 1e-6)
    vy = (y - prev_pos["y"]) / max(dt, 1e-6)
    vz = (z - prev_pos["z"]) / max(dt, 1e-6)
    STATE["position"] = {"x": x, "y": y, "z": z}
    STATE["velocity"] = {"x": vx, "y": vy, "z": vz}
    STATE["accel"] = {"x": (vx-prev_vel["x"])/max(dt,1e-6),
                      "y": (vy-prev_vel["y"])/max(dt,1e-6),
                      "z": (vz-prev_vel["z"])/max(dt,1e-6)}
    STATE["lengths"] = next_lengths
    STATE["physics"] = motor_metrics(STATE["position"], STATE["velocity"], STATE["accel"])
    STATE["updated_at"] = time.time()
    STATE["trail"].append({"x": x, "y": y, "z": z})
    if len(STATE["trail"]) > 250:
        STATE["trail"] = STATE["trail"][-250:]
    if STATE["recording"]["active"]:
        STATE["recording"]["points"].append({"x": x, "y": y, "z": z, "speed": STATE["speed"]})
        if len(STATE["recording"]["points"]) > 5000:
            STATE["recording"]["points"] = STATE["recording"]["points"][-5000:]

@app.on_event("startup")
async def startup():
    global motion_backend, executor, hardware_rt
    refresh_from_config()
    refresh_saved_paths()
    STATE["lengths"] = lengths_from_xyz(**STATE["position"])
    STATE["physics"] = motor_metrics(STATE["position"], STATE["velocity"], STATE["accel"])
    hardware_rt = HardwareRuntime(switch_map=cfg().limit_switches)
    motion_backend = build_backend(on_limit=handle_limit_event)
    executor = HardwareExecutor(motion_backend, cfg)
    STATE["mode"] = motion_backend.mode()
    asyncio.create_task(sim_loop())
    asyncio.create_task(push_loop())

@app.on_event("shutdown")
async def shutdown():
    if motion_backend:
        motion_backend.close()
    if hardware_rt:
        hardware_rt.close()

def handle_limit_event(axis: str, triggered: bool, tick: int):
    STATE["limit_switches"][axis] = triggered
    if triggered and motion_backend:
        motion_backend.stop()
        fault_mgr.set_fault("LIMIT_HIT", f"Limit switch triggered on axis {axis}", axis=axis)
        STATE["status"] = f"fault:limit:{axis}"
        STATE["estop"] = True

async def sim_loop():
    dt = 1 / 60
    while True:
        if not STATE["estop"]:
            px, py, pz = STATE["position"].values()
            tx, ty, tz = STATE["target"].values()
            dx, dy, dz = tx-px, ty-py, tz-pz
            dist = sqrt(dx*dx + dy*dy + dz*dz)
            if dist < 0.003:
                if STATE["path"]["points"]:
                    idx = STATE["path"]["index"] + 1
                    if idx < len(STATE["path"]["points"]):
                        STATE["path"]["index"] = idx
                        p = STATE["path"]["points"][idx]
                        set_target(p["x"], p["y"], p["z"], STATE["speed"])
                    else:
                        STATE["path"] = {"name": None, "index": 0, "points": []}
                        STATE["status"] = "idle"
                else:
                    STATE["status"] = "idle"
            else:
                step = STATE["speed"] * dt
                ratio = min(1.0, step / dist)
                apply_position(px + dx*ratio, py + dy*ratio, pz + dz*ratio, dt)
        await asyncio.sleep(dt)

async def push_loop():
    while True:
        refresh_from_config()
        refresh_saved_paths()
        STATE["fault_info"] = fault_mgr.get()
        if hardware_rt:
            STATE["limit_switches"] = hardware_rt.get_switch_states()
        await manager.broadcast({"type": "state", **STATE})
        await asyncio.sleep(1 / 20)

@app.get("/state")
def get_state():
    refresh_from_config()
    return STATE

@app.get("/config")
def get_config():
    return cfg()

@app.post("/config")
def post_config(cmd: ConfigUpdateCmd):
    try:
        new_cfg = SystemConfig.model_validate(cmd.config)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    save_config(new_cfg)
    refresh_from_config()
    return {"ok": True, "config": new_cfg}

@app.get("/wizard")
def wizard():
    return get_wizard_state()

@app.get("/wizard/checklist")
def wizard_checklist():
    return get_wizard_with_checklist()

@app.post("/wizard/step")
def wizard_step(cmd: WizardStepCmd):
    mark_step(cmd.step_id, cmd.done, cmd.notes)
    return {"ok": True}

@app.post("/wizard/reset")
def wizard_reset():
    reset_wizard()
    return {"ok": True}

@app.post("/wizard/motor-direction")
def wizard_motor_direction(cmd: DirectionCmd):
    set_motor_direction(cmd.axis, cmd.invert_dir, cmd.ok)
    homing_monitor.mark_direction_ok(cmd.axis, cmd.ok)
    refresh_from_config()
    return {"ok": True, "wizard": get_wizard_state()}

@app.post("/wizard/homed")
def wizard_homed(cmd: HomedCmd):
    set_homed(cmd.axis, cmd.homed)
    homing_monitor.mark_homed(cmd.axis, cmd.homed)
    refresh_from_config()
    return {"ok": True, "wizard": get_wizard_state()}

@app.post("/wizard/spool-radius")
def wizard_spool_radius(cmd: SpoolRadiusCmd):
    set_spool_radius(cmd.radius_m)
    homing_monitor.mark_spool_radius(True)
    refresh_from_config()
    return {"ok": True, "wizard": get_wizard_state()}

@app.post("/wizard/zero-lengths")
def wizard_zero_lengths(cmd: ZeroLengthsCmd):
    set_zero_lengths(cmd.lengths)
    homing_monitor.mark_center(True)
    refresh_from_config()
    return {"ok": True, "wizard": get_wizard_state()}

@app.post("/wizard/bounds")
def wizard_bounds(cmd: BoundsCmd):
    set_bounds(cmd.xmin, cmd.xmax, cmd.ymin, cmd.ymax, cmd.zmin, cmd.zmax)
    homing_monitor.mark_bounds(True)
    refresh_from_config()
    return {"ok": True, "wizard": get_wizard_state()}

@app.post("/move")
def move(target: Target):
    if STATE["estop"]: return {"ok": False, "error": "estop active"}
    if not within_bounds(target.x, target.y, target.z): return {"ok": False, "error": "out of bounds"}
    STATE["path"] = {"name": None, "index": 0, "points": []}
    set_target(target.x, target.y, target.z, target.speed)
    return {"ok": True, "target": STATE["target"]}

@app.post("/path")
def run_path(cmd: PathCmd):
    center = {"x": 1.0, "y": 1.0}
    if cmd.name == "square": pts = square_path(center, size=cmd.size, z=cmd.z)
    elif cmd.name == "circle": pts = circle_path(center, radius=cmd.radius, z=cmd.z)
    elif cmd.name == "diagonal": pts = diagonal_sweep(bounds(), z=cmd.z)
    else: return {"ok": False, "error": "unknown path"}
    set_path(cmd.name, pts)
    STATE["speed"] = cmd.speed
    return {"ok": True, "points": len(pts)}

@app.post("/stop")
def stop():
    if motion_backend: motion_backend.stop()
    p = STATE["position"]
    STATE["path"] = {"name": None, "index": 0, "points": []}
    set_target(p["x"], p["y"], p["z"], 0.4)
    STATE["status"] = "idle"
    return {"ok": True}

@app.post("/estop")
def estop():
    STATE["estop"] = True
    STATE["status"] = "stopped"
    if motion_backend: motion_backend.stop()
    return {"ok": True}

@app.post("/reset-estop")
def reset_estop():
    STATE["estop"] = False
    STATE["status"] = "idle"
    fault_mgr.clear()
    return {"ok": True}

@app.get("/faults")
def faults():
    return {"current": fault_mgr.get(), "history": fault_mgr.history()}

@app.post("/faults/reset")
def reset_faults():
    fault_mgr.clear()
    STATE["status"] = "idle"
    STATE["fault_info"] = fault_mgr.get()
    return {"ok": True}

@app.get("/switches")
def switches():
    if hardware_rt:
        STATE["limit_switches"] = hardware_rt.get_switch_states()
    return STATE["limit_switches"]

@app.post("/home/run")
def home_run(cmd: HomeCmd):
    if fault_mgr.active(): raise HTTPException(status_code=409, detail="Fault active")
    center = cfg().calibration.zero_lengths_m
    return {"ok": True, "message": "Homing sequence would run on real hardware"}

@app.post("/record/start")
def record_start():
    STATE["recording"] = {"active": True, "points": [], "started_at": time.time()}
    return {"ok": True}

@app.post("/record/stop")
def record_stop():
    STATE["recording"]["active"] = False
    return {"ok": True, "points": len(STATE["recording"]["points"])}

@app.post("/record/save")
def record_save(cmd: PathSaveCmd):
    payload = {"type": "waypoints", "speed": cmd.speed, "points": cmd.points}
    saved = upsert_path(cmd.name, payload)
    refresh_saved_paths()
    return {"ok": True, "path": saved}

@app.get("/paths")
def paths():
    refresh_saved_paths()
    return {"paths": STATE["saved_paths"], "poses": STATE["saved_poses"]}

@app.delete("/paths/{name}")
def path_delete(name: str):
    delete_path(name)
    refresh_saved_paths()
    return {"ok": True}

@app.post("/poses/save")
def pose_save(cmd: PoseSaveCmd):
    pose = upsert_pose(cmd.name, {"x": cmd.x, "y": cmd.y, "z": cmd.z})
    refresh_saved_paths()
    return {"ok": True, "pose": pose}

@app.post("/paths/replay/{name}")
def path_replay(name: str):
    refresh_saved_paths()
    path = STATE["saved_paths"].get(name)
    if not path: raise HTTPException(status_code=404, detail="Path not found")
    pts = path.get("points", [])
    if not pts: raise HTTPException(status_code=422, detail="Path has no points")
    set_path(name, pts)
    STATE["speed"] = float(path.get("speed", 0.25))
    return {"ok": True, "points": len(pts)}

@app.get("/profiles")
def get_profiles():
    return {"profiles": load_profiles(), "names": list_profiles()}

@app.post("/profiles/{name}/apply")
def apply_profile(name: str):
    profile = get_profile(name)
    if not profile: raise HTTPException(status_code=404, detail="Profile not found")
    try:
        new_cfg = SystemConfig.model_validate(profile)
        save_config(new_cfg)
        refresh_from_config()
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"ok": True, "applied": name}

@app.post("/profiles/save-current")
def save_current_profile(cmd: ProfileSaveCmd):
    current = cfg()
    save_profile(cmd.name, current.model_dump(mode="python"))
    return {"ok": True, "name": cmd.name}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    await ws.send_text(json.dumps({"type": "state", **STATE}))
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")
            if msg_type == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
            elif msg_type == "jog" and not STATE["estop"]:
                dx, dy, dz = float(data.get("dx",0)), float(data.get("dy",0)), float(data.get("dz",0))
                speed = float(data.get("speed", 0.4))
                px, py, pz = STATE["position"].values()
                STATE["path"] = {"name": None, "index": 0, "points": []}
                set_target(px+dx, py+dy, pz+dz, speed)
            elif msg_type == "move" and not STATE["estop"]:
                x, y, z = float(data["x"]), float(data["y"]), float(data["z"])
                speed = float(data.get("speed", 0.4))
                if within_bounds(x, y, z):
                    STATE["path"] = {"name": None, "index": 0, "points": []}
                    set_target(x, y, z, speed)
            elif msg_type == "preset" and not STATE["estop"]:
                name = data.get("name")
                presets = {
                    "center": {"x": 1.0, "y": 1.0, "z": 0.9},
                    "low_center": {"x": 1.0, "y": 1.0, "z": 0.5},
                    "front_left": {"x": 0.4, "y": 0.4, "z": 0.9},
                    "front_right": {"x": 1.6, "y": 0.4, "z": 0.9},
                    "rear_left": {"x": 0.4, "y": 1.6, "z": 0.9},
                    "rear_right": {"x": 1.6, "y": 1.6, "z": 0.9},
                }
                if name in presets:
                    t = presets[name]
                    STATE["path"] = {"name": None, "index": 0, "points": []}
                    set_target(t["x"], t["y"], t["z"], float(data.get("speed", 0.4)))
            elif msg_type == "path" and not STATE["estop"]:
                name = data.get("name")
                speed = float(data.get("speed", 0.35))
                z = float(data.get("z", 0.9))
                if name == "square": pts = square_path({"x":1.0,"y":1.0}, size=float(data.get("size",0.8)), z=z)
                elif name == "circle": pts = circle_path({"x":1.0,"y":1.0}, radius=float(data.get("radius",0.45)), z=z)
                elif name == "diagonal": pts = diagonal_sweep(bounds(), z=z)
                else: pts = []
                if pts:
                    STATE["speed"] = speed
                    set_path(name, pts)
            elif msg_type == "home" and not STATE["estop"]:
                set_target(1.0, 1.0, 0.9, 0.4)
            elif msg_type == "stop":
                p = STATE["position"]
                STATE["path"] = {"name": None, "index": 0, "points": []}
                set_target(p["x"], p["y"], p["z"], STATE["speed"])
                STATE["status"] = "idle"
            elif msg_type == "estop":
                STATE["estop"] = True
                STATE["status"] = "stopped"
            elif msg_type == "reset-estop":
                STATE["estop"] = False
                STATE["status"] = "idle"
                fault_mgr.clear()
    except WebSocketDisconnect:
        manager.disconnect(ws)
