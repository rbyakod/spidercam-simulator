from __future__ import annotations

import asyncio
import fcntl
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from controllers.sim_controller import SimController
from executor import MotionExecutor
from models import PathCmd, Target, build_runtime_context
from persistent_config import load_config
from planner import circle_path, square_path
from runtime_store import RuntimeStore

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

cfg = load_config()
context = build_runtime_context(cfg)
store = RuntimeStore(context)
controller = SimController(context)
executor = MotionExecutor(context, controller)
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


def with_state_lock(mutator=None):
    return store.with_state_lock(mutator)

@app.on_event("startup")
async def startup():
    global leader_fd
    with_state_lock()
    leader_fd = open(store.leader_lock_path, "a+")
    try:
        fcntl.flock(leader_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        asyncio.create_task(sim_loop())
        asyncio.create_task(push_loop())
    except BlockingIOError:
        pass


def resolve_path_points(cmd_name: str, size: float, radius: float, z: float):
    if cmd_name == "square":
        return square_path({"x": 1.0, "y": 1.0}, size=size, z=z)
    if cmd_name == "circle":
        return circle_path({"x": 1.0, "y": 1.0}, radius=radius, z=z)
    return []

async def sim_loop():
    dt = 1/60
    while True:
        with_state_lock(lambda state: executor.advance_state(state, dt))
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
    result = {"ok": True}
    def mutate(state):
        executor.clear_path(state)
        result.update(executor.set_target(state, target.x, target.y, target.z, target.speed))
    with_state_lock(mutate)
    return result

@app.post('/path')
def run_path(cmd: PathCmd):
    pts = resolve_path_points(cmd.name, cmd.size, cmd.radius, cmd.z)
    if not pts:
        return {"ok": False, "error": 'unknown path'}
    result = {"ok": True}
    def mutate(state):
        result.update(executor.queue_path(state, cmd.name, pts, cmd.speed))
    with_state_lock(mutate)
    return {**result, "points": len(pts)}

@app.post('/stop')
def stop():
    with_state_lock(executor.stop)
    return {"ok": True}

@app.post('/estop')
def estop():
    with_state_lock(executor.estop)
    return {"ok": True}

@app.post('/reset-estop')
def reset_estop():
    with_state_lock(executor.reset_estop)
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
                    executor.set_target(
                        state,
                        px + float(data.get('dx', 0)),
                        py + float(data.get('dy', 0)),
                        pz + float(data.get('dz', 0)),
                        float(data.get('speed', 0.4)),
                    )
                with_state_lock(mutate)
            elif t == 'move':
                def mutate(state):
                    if state["estop"]:
                        return
                    executor.set_target(
                        state,
                        float(data['x']),
                        float(data['y']),
                        float(data['z']),
                        float(data.get('speed', 0.4)),
                    )
                with_state_lock(mutate)
            elif t == 'path':
                name = str(data.get('name'))
                pts = resolve_path_points(
                    name,
                    float(data.get('size', 0.8)),
                    float(data.get('radius', 0.45)),
                    float(data.get('z', 0.9)),
                )
                def mutate(state):
                    if state["estop"] or not pts:
                        return
                    executor.queue_path(state, name, pts, float(data.get('speed', 0.35)))
                with_state_lock(mutate)
            elif t == 'stop':
                with_state_lock(executor.stop)
            elif t == 'estop':
                with_state_lock(executor.estop)
            elif t == 'reset-estop':
                with_state_lock(executor.reset_estop)
    except WebSocketDisconnect:
        manager.disconnect(ws)
