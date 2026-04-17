from __future__ import annotations
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from math import sqrt, pi
import asyncio, json, time
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

STATE = {
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
STATE["lengths"] = lengths_from_xyz(**STATE["position"])

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
    asyncio.create_task(sim_loop())
    asyncio.create_task(push_loop())

def set_target(x: float, y: float, z: float, speed: float):
    x = max(bounds["x"][0], min(bounds["x"][1], x))
    y = max(bounds["y"][0], min(bounds["y"][1], y))
    z = max(bounds["z"][0], min(bounds["z"][1], z))
    STATE["target"] = {"x": x, "y": y, "z": z}
    STATE["speed"] = max(0.05, min(speed, 1.0))
    STATE["status"] = "moving"

async def sim_loop():
    dt = 1/60
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
                nx, ny, nz = px + dx*ratio, py + dy*ratio, pz + dz*ratio
                prev = STATE["lengths"]
                nxt = lengths_from_xyz(nx, ny, nz)
                for k in nxt:
                    dl = nxt[k] - prev[k]
                    STATE["steps"][k] += steps_from_delta_length(dl)
                    STATE["spools"][k] += dl / spool_radius
                STATE["position"] = {"x": nx, "y": ny, "z": nz}
                STATE["lengths"] = nxt
                STATE["updated_at"] = time.time()
                STATE["trail"].append({"x": nx, "y": ny, "z": nz})
                STATE["trail"] = STATE["trail"][-250:]
        await asyncio.sleep(dt)

async def push_loop():
    while True:
        await manager.broadcast({"type": "state", **STATE})
        await asyncio.sleep(1/20)

@app.get('/state')
def get_state():
    return STATE

@app.post('/move')
def move(target: Target):
    STATE["path"] = {"name": None, "index": 0, "points": []}
    set_target(target.x, target.y, target.z, target.speed)
    return {"ok": True}

@app.post('/path')
def run_path(cmd: PathCmd):
    if cmd.name == 'square':
        pts = square_path({"x": 1.0, "y": 1.0}, size=cmd.size, z=cmd.z)
    elif cmd.name == 'circle':
        pts = circle_path({"x": 1.0, "y": 1.0}, radius=cmd.radius, z=cmd.z)
    else:
        return {"ok": False, "error": 'unknown path'}
    STATE["path"] = {"name": cmd.name, "index": 0, "points": pts}
    STATE["speed"] = cmd.speed
    if pts:
        set_target(pts[0]["x"], pts[0]["y"], pts[0]["z"], cmd.speed)
    return {"ok": True, "points": len(pts)}

@app.post('/stop')
def stop():
    STATE["path"] = {"name": None, "index": 0, "points": []}
    STATE["target"] = dict(STATE["position"])
    STATE["status"] = 'idle'
    return {"ok": True}

@app.post('/estop')
def estop():
    STATE["estop"] = True
    STATE["status"] = 'stopped'
    return {"ok": True}

@app.post('/reset-estop')
def reset_estop():
    STATE["estop"] = False
    STATE["status"] = 'idle'
    return {"ok": True}

@app.websocket('/ws')
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)
    await ws.send_text(json.dumps({"type": "state", **STATE}))
    try:
        while True:
            data = await ws.receive_json()
            t = data.get('type')
            if t == 'jog' and not STATE["estop"]:
                px, py, pz = STATE["position"].values()
                set_target(px + float(data.get('dx', 0)), py + float(data.get('dy', 0)), pz + float(data.get('dz', 0)), float(data.get('speed', 0.4)))
            elif t == 'move' and not STATE["estop"]:
                set_target(float(data['x']), float(data['y']), float(data['z']), float(data.get('speed', 0.4)))
            elif t == 'path' and not STATE["estop"]:
                name = data.get('name')
                if name == 'square':
                    pts = square_path({"x": 1.0, "y": 1.0}, size=float(data.get('size', 0.8)), z=float(data.get('z', 0.9)))
                elif name == 'circle':
                    pts = circle_path({"x": 1.0, "y": 1.0}, radius=float(data.get('radius', 0.45)), z=float(data.get('z', 0.9)))
                else:
                    pts = []
                if pts:
                    STATE["path"] = {"name": name, "index": 0, "points": pts}
                    STATE["speed"] = float(data.get('speed', 0.35))
                    set_target(pts[0]["x"], pts[0]["y"], pts[0]["z"], STATE["speed"])
            elif t == 'stop':
                STATE["path"] = {"name": None, "index": 0, "points": []}
                STATE["target"] = dict(STATE["position"])
                STATE["status"] = 'idle'
            elif t == 'estop':
                STATE["estop"] = True
                STATE["status"] = 'stopped'
            elif t == 'reset-estop':
                STATE["estop"] = False
                STATE["status"] = 'idle'
    except WebSocketDisconnect:
        manager.disconnect(ws)
