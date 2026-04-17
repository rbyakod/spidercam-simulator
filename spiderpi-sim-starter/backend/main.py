from __future__ import annotations
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from math import sqrt, pi
from pathlib import Path
import asyncio, fcntl, json, os, tempfile, time
from persistent_config import load_config
from planner import square_path, circle_path

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

cfg = load_config()
anchors = cfg.frame.anchors
bounds = cfg.frame.bounds
spool_radius = cfg.frame.spool_radius_m
motor_steps_per_rev = cfg.frame.motor_steps_per_rev
microsteps = cfg.motors.microsteps
DATA_DIR = Path("data")
STATE_PATH = DATA_DIR / "runtime_state.json"
STATE_LOCK_PATH = DATA_DIR / "runtime_state.lock"
LEADER_LOCK_PATH = DATA_DIR / "sim_loop.lock"
DATA_DIR.mkdir(parents=True, exist_ok=True)
leader_fd = None

class Manager:
    def __init__(self):
        self.clients = set()
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

def lengths_from_xyz(x: float, y: float, z: float):
    out = {}
    for name, (ax, ay, az) in anchors.items():
        out[name] = sqrt((x-ax)**2 + (y-ay)**2 + (z-az)**2)
    return out

def steps_from_delta_length(delta_len: float) -> int:
    revs = delta_len / (2 * pi * spool_radius)
    return int(revs * motor_steps_per_rev * microsteps)

def default_state():
    state = {
        "mode": "sim",
        "status": "idle",
        "estop": False,
        "position": {"x": 1.0, "y": 1.0, "z": 0.9},
        "target": {"x": 1.0, "y": 1.0, "z": 0.9},
        "speed": 0.4,
        "anchors": anchors,
        "bounds": bounds,
        "lengths": {},
        "steps": {"A": 0, "B": 0, "C": 0, "D": 0},
        "spools": {"A": 0.0, "B": 0.0, "C": 0.0, "D": 0.0},
        "trail": [],
        "path": {"name": None, "index": 0, "points": []},
        "updated_at": time.time(),
    }
    state["lengths"] = lengths_from_xyz(**state["position"])
    return state

def read_state_unlocked():
    if not STATE_PATH.exists():
        state = default_state()
        write_state_unlocked(state)
        return state
    raw = json.loads(STATE_PATH.read_text())
    raw["anchors"] = anchors
    raw["bounds"] = bounds
    return raw

def write_state_unlocked(state: dict):
    payload = json.dumps(state)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(DATA_DIR), suffix=".tmp") as tf:
        tf.write(payload)
        temp_name = tf.name
    os.replace(temp_name, STATE_PATH)

def with_state_lock(mutator=None):
    with open(STATE_LOCK_PATH, "a+") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        state = read_state_unlocked()
        if mutator is not None:
            mutator(state)
            write_state_unlocked(state)
        return state

class Target(BaseModel):
    x: float
    y: float
    z: float
    speed: float = 0.4

class PathCmd(BaseModel):
    name: str
    speed: float = 0.35
    size: float = 0.8
    radius: float = 0.45
    z: float = 0.9

@app.on_event("startup")
async def startup():
    global leader_fd
    with_state_lock()
    leader_fd = open(LEADER_LOCK_PATH, "a+")
    try:
        fcntl.flock(leader_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        asyncio.create_task(sim_loop())
        asyncio.create_task(push_loop())
    except BlockingIOError:
        pass

def set_target(state: dict, x: float, y: float, z: float, speed: float):
    x = max(bounds["x"][0], min(bounds["x"][1], x))
    y = max(bounds["y"][0], min(bounds["y"][1], y))
    z = max(bounds["z"][0], min(bounds["z"][1], z))
    state["target"] = {"x": x, "y": y, "z": z}
    state["speed"] = max(0.05, min(speed, 1.0))
    state["status"] = "moving"

def advance_state(state: dict, dt: float):
    if state["estop"]:
        return
    px, py, pz = state["position"].values()
    tx, ty, tz = state["target"].values()
    dx, dy, dz = tx-px, ty-py, tz-pz
    dist = sqrt(dx*dx + dy*dy + dz*dz)
    if dist < 0.003:
        if state["path"]["points"]:
            idx = state["path"]["index"] + 1
            if idx < len(state["path"]["points"]):
                state["path"]["index"] = idx
                p = state["path"]["points"][idx]
                set_target(state, p["x"], p["y"], p["z"], state["speed"])
            else:
                state["path"] = {"name": None, "index": 0, "points": []}
                state["status"] = "idle"
        else:
            state["status"] = "idle"
        return
    step = state["speed"] * dt
    ratio = min(1.0, step / dist)
    nx, ny, nz = px + dx*ratio, py + dy*ratio, pz + dz*ratio
    prev = state["lengths"]
    nxt = lengths_from_xyz(nx, ny, nz)
    for k in nxt:
        dl = nxt[k] - prev[k]
        state["steps"][k] += steps_from_delta_length(dl)
        state["spools"][k] += dl / spool_radius
    state["position"] = {"x": nx, "y": ny, "z": nz}
    state["lengths"] = nxt
    state["updated_at"] = time.time()
    state["trail"].append({"x": nx, "y": ny, "z": nz})
    state["trail"] = state["trail"][-250:]

async def sim_loop():
    dt = 1/60
    while True:
        with_state_lock(lambda state: advance_state(state, dt))
        await asyncio.sleep(dt)

async def push_loop():
    while True:
        state = with_state_lock()
        await manager.broadcast({"type": "state", **state})
        await asyncio.sleep(1/20)

@app.get('/state')
def get_state():
    return with_state_lock()

@app.post('/move')
def move(target: Target):
    def mutate(state):
        state["path"] = {"name": None, "index": 0, "points": []}
        set_target(state, target.x, target.y, target.z, target.speed)
    with_state_lock(mutate)
    return {"ok": True}

@app.post('/path')
def run_path(cmd: PathCmd):
    if cmd.name == 'square':
        pts = square_path({"x": 1.0, "y": 1.0}, size=cmd.size, z=cmd.z)
    elif cmd.name == 'circle':
        pts = circle_path({"x": 1.0, "y": 1.0}, radius=cmd.radius, z=cmd.z)
    else:
        return {"ok": False, "error": 'unknown path'}
    def mutate(state):
        state["path"] = {"name": cmd.name, "index": 0, "points": pts}
        state["speed"] = cmd.speed
        if pts:
            set_target(state, pts[0]["x"], pts[0]["y"], pts[0]["z"], cmd.speed)
    with_state_lock(mutate)
    return {"ok": True, "points": len(pts)}

@app.post('/stop')
def stop():
    def mutate(state):
        state["path"] = {"name": None, "index": 0, "points": []}
        state["target"] = dict(state["position"])
        state["status"] = 'idle'
    with_state_lock(mutate)
    return {"ok": True}

@app.post('/estop')
def estop():
    def mutate(state):
        state["estop"] = True
        state["status"] = 'stopped'
    with_state_lock(mutate)
    return {"ok": True}

@app.post('/reset-estop')
def reset_estop():
    def mutate(state):
        state["estop"] = False
        state["status"] = 'idle'
    with_state_lock(mutate)
    return {"ok": True}

@app.websocket('/ws')
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)
    await ws.send_text(json.dumps({"type": "state", **with_state_lock()}))
    try:
        while True:
            data = await ws.receive_json()
            t = data.get('type')
            if t == 'jog':
                def mutate(state):
                    if state["estop"]:
                        return
                    px, py, pz = state["position"].values()
                    set_target(state, px + float(data.get('dx', 0)), py + float(data.get('dy', 0)), pz + float(data.get('dz', 0)), float(data.get('speed', 0.4)))
                with_state_lock(mutate)
            elif t == 'move':
                def mutate(state):
                    if state["estop"]:
                        return
                    set_target(state, float(data['x']), float(data['y']), float(data['z']), float(data.get('speed', 0.4)))
                with_state_lock(mutate)
            elif t == 'path':
                name = data.get('name')
                if name == 'square':
                    pts = square_path({"x": 1.0, "y": 1.0}, size=float(data.get('size', 0.8)), z=float(data.get('z', 0.9)))
                elif name == 'circle':
                    pts = circle_path({"x": 1.0, "y": 1.0}, radius=float(data.get('radius', 0.45)), z=float(data.get('z', 0.9)))
                else:
                    pts = []
                def mutate(state):
                    if state["estop"] or not pts:
                        return
                    state["path"] = {"name": name, "index": 0, "points": pts}
                    state["speed"] = float(data.get('speed', 0.35))
                    set_target(state, pts[0]["x"], pts[0]["y"], pts[0]["z"], state["speed"])
                with_state_lock(mutate)
            elif t == 'stop':
                def mutate(state):
                    state["path"] = {"name": None, "index": 0, "points": []}
                    state["target"] = dict(state["position"])
                    state["status"] = 'idle'
                with_state_lock(mutate)
            elif t == 'estop':
                def mutate(state):
                    state["estop"] = True
                    state["status"] = 'stopped'
                with_state_lock(mutate)
            elif t == 'reset-estop':
                def mutate(state):
                    state["estop"] = False
                    state["status"] = 'idle'
                with_state_lock(mutate)
    except WebSocketDisconnect:
        manager.disconnect(ws)
