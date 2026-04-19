from __future__ import annotations

from math import sqrt
from typing import Dict

from models import RuntimeContext
from workspace import clamp_target


class MotionExecutor:
    def __init__(self, context: RuntimeContext, controller):
        self.context = context
        self.controller = controller

    def set_target(self, state: Dict[str, object], x: float, y: float, z: float, speed: float) -> None:
        state["target"] = clamp_target(self.context, x, y, z)
        state["speed"] = max(0.05, min(speed, 1.0))
        state["status"] = "moving"
        state["controller_ready"] = self.controller.is_ready()

    def clear_path(self, state: Dict[str, object]) -> None:
        state["path"] = {"name": None, "index": 0, "points": []}

    def queue_path(self, state: Dict[str, object], name: str, points, speed: float) -> None:
        state["path"] = {"name": name, "index": 0, "points": points}
        state["speed"] = speed
        if points:
            first = points[0]
            self.set_target(state, first["x"], first["y"], first["z"], speed)

    def stop(self, state: Dict[str, object]) -> None:
        self.clear_path(state)
        state["target"] = dict(state["position"])
        state["status"] = "idle"

    def estop(self, state: Dict[str, object]) -> None:
        state["estop"] = True
        state["status"] = "estopped"

    def reset_estop(self, state: Dict[str, object]) -> None:
        state["estop"] = False
        state["status"] = "idle"

    def advance_state(self, state: Dict[str, object], dt: float) -> None:
        state["controller_ready"] = self.controller.is_ready()
        if state["estop"]:
            state["status"] = "estopped"
            return

        px, py, pz = state["position"].values()
        tx, ty, tz = state["target"].values()
        dx, dy, dz = tx - px, ty - py, tz - pz
        dist = sqrt(dx * dx + dy * dy + dz * dz)

        if dist < 0.003:
            path_state = state["path"]
            if path_state["points"]:
                idx = path_state["index"] + 1
                if idx < len(path_state["points"]):
                    path_state["index"] = idx
                    point = path_state["points"][idx]
                    self.set_target(state, point["x"], point["y"], point["z"], state["speed"])
                else:
                    self.clear_path(state)
                    state["status"] = "idle"
            else:
                state["status"] = "idle"
            return

        step = state["speed"] * dt
        ratio = min(1.0, step / dist)
        next_position = {
            "x": px + dx * ratio,
            "y": py + dy * ratio,
            "z": pz + dz * ratio,
        }
        self.controller.apply_pose(state, next_position)
