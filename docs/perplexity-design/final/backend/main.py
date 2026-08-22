from __future__ import annotations
import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
from motion_backend import motion
from physics import inverse_kinematics, check_tensions
from faults import fault_manager, FaultCode
from calibration import calibration
from calibration_state import cal_state, CalibrationStep
from homing import homing
from homing_monitor import homing_monitor
from path_store import path_store
from motion_profile import profile_store, MotionProfile
from gpio_backend import load_gpio_map, save_gpio_map
from hardware_runtime import hardware_loop
from ramped_scheduler import RampedScheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(hardware_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(title="SpiderCAM API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self) -> None:
        self.active = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self.active.remove(ws)

    async def broadcast(self, data: dict) -> None:
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active.remove(ws)

manager = ConnectionManager()

@app.websocket("/ws/telemetry")
async def ws_telemetry(ws: WebSocket):
    await manager.connect(ws)
    scheduler = RampedScheduler(target_hz=settings.ws_tick_hz)
    try:
        while True:
            status = motion.status()
            status["timestamp"] = time.time()
            status["faults"] = fault_manager.active()
            status["homing"] = homing.to_dict()
            status["calibration"] = cal_state.to_dict()
            await ws.send_json(status)
            await scheduler.tick()
    except WebSocketDisconnect:
        manager.disconnect(ws)

class MoveRequest(BaseModel):
    x: float
    y: float
    z: float
    payload_kg: float = 0.5

class JogRequest(BaseModel):
    axis: int
    distance: float
    speed: float = 0.1

@app.post("/api/move")
async def api_move(req: MoveRequest):
    ok, reason = homing_monitor.check()
    if not ok:
        raise HTTPException(400, reason)
    result = await motion.move_to([req.x, req.y, req.z], req.payload_kg)
    if not result["success"]:
        raise HTTPException(400, result["reason"])
    return result

@app.post("/api/jog")
async def api_jog(req: JogRequest):
    pos = motion.current_pos.copy()
    if req.axis == 0:
        pos[0] += req.distance
    elif req.axis == 1:
        pos[1] += req.distance
    elif req.axis == 2:
        pos[2] += req.distance
    result = await motion.move_to(pos.tolist())
    return result

@app.post("/api/estop")
async def api_estop():
    fault_manager.raise_fault(FaultCode.NONE, "E-stop triggered by operator")
    fault_manager.e_stop = True
    return {"e_stop": True}

@app.post("/api/fault/clear")
async def api_fault_clear():
    fault_manager.clear()
    return {"e_stop": False}

@app.get("/api/status")
async def api_status():
    return motion.status()

class PathRequest(BaseModel):
    name: str
    waypoints: list

@app.get("/api/paths")
async def list_paths():
    return {"paths": path_store.list()}

@app.post("/api/paths")
async def save_path(req: PathRequest):
    path_store.save(req.name, req.waypoints)
    return {"saved": req.name}

@app.post("/api/paths/{name}/run")
async def run_path(name: str):
    waypoints = path_store.get(name)
    if not waypoints:
        raise HTTPException(404, f"Path '{name}' not found")
    results = []
    for wp in waypoints:
        r = await motion.move_to(wp)
        results.append(r)
    return {"results": results}

@app.delete("/api/paths/{name}")
async def delete_path(name: str):
    ok = path_store.delete(name)
    return {"deleted": ok}

@app.post("/api/home")
async def api_home():
    from hardware_executor import executor
    ok = await homing.home_all(executor)
    if not ok:
        raise HTTPException(500, "Homing failed")
    return homing.to_dict()

@app.get("/api/home/status")
async def api_home_status():
    return homing.to_dict()

class CalibrateRequest(BaseModel):
    measured_lengths: list

@app.post("/api/calibrate")
async def api_calibrate(req: CalibrateRequest):
    offsets = calibration.compute_offsets(req.measured_lengths)
    cal_state.step = CalibrationStep.DONE
    cal_state.is_calibrated = True
    cal_state.offsets = offsets.tolist()
    return calibration.to_dict()

@app.get("/api/calibrate/status")
async def api_calibrate_status():
    return cal_state.to_dict()

@app.get("/api/profiles")
async def list_profiles():
    return {"profiles": profile_store.list()}

class ProfileRequest(BaseModel):
    name: str
    max_speed: float
    max_accel: float
    jerk_limit: float = None
    description: str = ""

@app.post("/api/profiles")
async def save_profile(req: ProfileRequest):
    p = MotionProfile(**req.dict())
    profile_store.save(p)
    return p.to_dict()

@app.delete("/api/profiles/{name}")
async def delete_profile(name: str):
    ok = profile_store.delete(name)
    return {"deleted": ok}

@app.get("/api/gpio")
async def get_gpio():
    return load_gpio_map()

@app.post("/api/gpio")
async def set_gpio(gpio_map: dict):
    save_gpio_map(gpio_map)
    return {"saved": True}

@app.get("/health")
async def health():
    return {"status": "ok", "sim": settings.sim_mode}
