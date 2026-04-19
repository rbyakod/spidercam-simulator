from __future__ import annotations

import asyncio
import fcntl
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from controllers.controller_manager import ControllerManager
from controllers.dry_run_controller import DryRunController
from controllers.hardware_controller import HardwareController
from controllers.sim_controller import SimController
from executor import MotionExecutor
from models import ModeCmd, PathCmd, Target, build_runtime_context
from persistent_config import load_config
from planner import circle_path, square_path
from runtime_store import RuntimeStore

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

cfg = load_config()
context = build_runtime_context(cfg)
store = RuntimeStore(context)
controller_manager = ControllerManager({
    "sim": SimController(context),
    "dry_run": DryRunController(context),
    "hardware": HardwareController(context),
})
executor = MotionExecutor(context, controller_manager)
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
        for client in dead:
            self.disconnect(client)


manager = Manager()


def with_state_lock(mutator=None):
    return store.with_state_lock(mutator)


def current_state():
    state = with_state_lock()
    executor.sync_state(state)
    return state


@app.on_event("startup")
async def startup():
    global leader_fd
    with_state_lock(executor.sync_state)
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
    dt = 1 / 60
    while True:
        with_state_lock(lambda state: executor.advance_state(state, dt))
        await asyncio.sleep(dt)


async def push_loop():
    while True:
        await manager.broadcast({"type": "state", **current_state()})
        await asyncio.sleep(1 / 20)


@app.get("/state")
def get_state():
    return current_state()


@app.post("/mode")
def set_mode(cmd: ModeCmd):
    result = {"ok": True}

    def mutate(state):
        result.update(executor.set_mode(state, cmd.mode))

    with_state_lock(mutate)
    return result


@app.post("/arm")
def arm():
    result = {"ok": True}
    with_state_lock(lambda state: result.update(executor.arm(state)))
    return result


@app.post("/disarm")
def disarm():
    result = {"ok": True}
    with_state_lock(lambda state: result.update(executor.disarm(state)))
    return result


@app.post("/home")
def home():
    result = {"ok": True}
    with_state_lock(lambda state: result.update(executor.home(state)))
    return result


@app.post("/verify-limits")
def verify_limits():
    result = {"ok": True}
    with_state_lock(lambda state: result.update(executor.verify_limits(state)))
    return result


@app.post("/verify-motor-directions")
def verify_motor_directions():
    result = {"ok": True}
    with_state_lock(lambda state: result.update(executor.verify_motor_directions(state)))
    return result


@app.post("/calibrate")
def calibrate():
    result = {"ok": True}
    with_state_lock(lambda state: result.update(executor.calibrate(state)))
    return result


@app.post("/move")
def move(target: Target):
    result = {"ok": True}

    def mutate(state):
        executor.clear_path(state)
        result.update(executor.set_target(state, target.x, target.y, target.z, target.speed))

    with_state_lock(mutate)
    return result


@app.post("/path")
def run_path(cmd: PathCmd):
    points = resolve_path_points(cmd.name, cmd.size, cmd.radius, cmd.z)
    if not points:
        return {"ok": False, "error": "unknown path"}
    result = {"ok": True}

    def mutate(state):
        result.update(executor.queue_path(state, cmd.name, points, cmd.speed))

    with_state_lock(mutate)
    return {**result, "points": len(points)}


@app.post("/stop")
def stop():
    with_state_lock(executor.stop)
    return {"ok": True}


@app.post("/estop")
def estop():
    with_state_lock(executor.estop)
    return {"ok": True}


@app.post("/reset-estop")
def reset_estop():
    result = {"ok": True}
    with_state_lock(lambda state: result.update(executor.reset_estop(state)))
    return result


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)
    await ws.send_text(json.dumps({"type": "state", **current_state()}))
    try:
        while True:
            data = await ws.receive_json()
            command_type = data.get("type")

            if command_type == "move":
                with_state_lock(
                    lambda state: executor.set_target(
                        state,
                        float(data["x"]),
                        float(data["y"]),
                        float(data["z"]),
                        float(data.get("speed", 0.4)),
                    )
                )
            elif command_type == "jog":
                def mutate(state):
                    px, py, pz = state["position"].values()
                    executor.set_target(
                        state,
                        px + float(data.get("dx", 0)),
                        py + float(data.get("dy", 0)),
                        pz + float(data.get("dz", 0)),
                        float(data.get("speed", 0.4)),
                    )

                with_state_lock(mutate)
            elif command_type == "path":
                name = str(data.get("name"))
                points = resolve_path_points(
                    name,
                    float(data.get("size", 0.8)),
                    float(data.get("radius", 0.45)),
                    float(data.get("z", 0.9)),
                )
                with_state_lock(lambda state: executor.queue_path(state, name, points, float(data.get("speed", 0.35))))
            elif command_type == "mode":
                with_state_lock(lambda state: executor.set_mode(state, str(data.get("mode", "sim"))))
            elif command_type == "arm":
                with_state_lock(lambda state: executor.arm(state))
            elif command_type == "disarm":
                with_state_lock(lambda state: executor.disarm(state))
            elif command_type == "home":
                with_state_lock(lambda state: executor.home(state))
            elif command_type == "verify-limits":
                with_state_lock(lambda state: executor.verify_limits(state))
            elif command_type == "verify-motor-directions":
                with_state_lock(lambda state: executor.verify_motor_directions(state))
            elif command_type == "calibrate":
                with_state_lock(lambda state: executor.calibrate(state))
            elif command_type == "stop":
                with_state_lock(executor.stop)
            elif command_type == "estop":
                with_state_lock(executor.estop)
            elif command_type == "reset-estop":
                with_state_lock(lambda state: executor.reset_estop(state))
    except WebSocketDisconnect:
        manager.disconnect(ws)
