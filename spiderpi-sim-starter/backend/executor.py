from __future__ import annotations

from math import sqrt
from typing import Dict

from models import RuntimeContext
from workspace import validate_target


class MotionExecutor:
    def __init__(self, context: RuntimeContext, controller):
        self.context = context
        self.controller = controller

    def _set_last_error(self, state: Dict[str, object], errors: list[str]) -> None:
        state["last_error"] = ", ".join(errors)

    def _clear_last_error(self, state: Dict[str, object]) -> None:
        state["last_error"] = None

    def _set_current_as_target(self, state: Dict[str, object]) -> None:
        state["target"] = dict(state["position"])
        state["target_lengths"] = dict(state["lengths"])

    def set_target(self, state: Dict[str, object], x: float, y: float, z: float, speed: float) -> Dict[str, object]:
        validation = validate_target(self.context, x, y, z)
        if not validation["valid"]:
            self._set_last_error(state, validation["errors"])
            return {"ok": False, "errors": validation["errors"]}

        self._clear_last_error(state)
        state["target"] = {"x": float(x), "y": float(y), "z": float(z)}
        state["target_lengths"] = dict(validation["lengths"])
        state["controller_ready"] = self.controller.is_ready()
        state["workspace_valid"] = True
        state["speed"] = max(0.05, min(speed, 1.0))
        state["status"] = "moving"
        return {"ok": True}

    def clear_path(self, state: Dict[str, object]) -> None:
        state["path"] = {"name": None, "index": 0, "points": []}

    def queue_path(self, state: Dict[str, object], name: str, points, speed: float) -> Dict[str, object]:
        for index, point in enumerate(points):
            validation = validate_target(self.context, point["x"], point["y"], point["z"])
            if not validation["valid"]:
                errors = [f"path_point_{index}:{error}" for error in validation["errors"]]
                self._set_last_error(state, errors)
                return {"ok": False, "errors": errors}

        self._clear_last_error(state)
        state["path"] = {"name": name, "index": 0, "points": points}
        state["speed"] = speed
        if points:
            first = points[0]
            return self.set_target(state, first["x"], first["y"], first["z"], speed)
        return {"ok": True}

    def stop(self, state: Dict[str, object]) -> None:
        self.clear_path(state)
        self._clear_last_error(state)
        self._set_current_as_target(state)
        state["status"] = "idle"

    def estop(self, state: Dict[str, object]) -> None:
        state["estop"] = True
        state["status"] = "estopped"

    def reset_estop(self, state: Dict[str, object]) -> None:
        state["estop"] = False
        self._clear_last_error(state)
        state["status"] = "idle"

    def advance_state(self, state: Dict[str, object], dt: float) -> None:
        state["controller_ready"] = self.controller.is_ready()
        if state["estop"]:
            state["status"] = "estopped"
            return

        px, py, pz = state["position"].values()
        tx, ty, tz = state["target"].values()
        dx, dy, dz = tx - px, ty - py, tz - pz
        cartesian_dist = sqrt(dx * dx + dy * dy + dz * dz)
        current_lengths = state["lengths"]
        target_lengths = state["target_lengths"]
        cable_dist = sqrt(
            sum((target_lengths[name] - current_lengths[name]) ** 2 for name in self.context.cable_names)
        )

        if cartesian_dist < 0.003 or cable_dist < 0.003:
            path_state = state["path"]
            if path_state["points"]:
                idx = path_state["index"] + 1
                if idx < len(path_state["points"]):
                    path_state["index"] = idx
                    point = path_state["points"][idx]
                    result = self.set_target(state, point["x"], point["y"], point["z"], state["speed"])
                    if not result["ok"]:
                        self.clear_path(state)
                        self._set_current_as_target(state)
                        state["status"] = "idle"
                else:
                    self.clear_path(state)
                    self._set_current_as_target(state)
                    state["status"] = "idle"
            else:
                state["status"] = "idle"
            return

        step = state["speed"] * dt
        ratio = min(1.0, step / cartesian_dist) if cartesian_dist > 1e-9 else 1.0
        next_lengths = {
            name: current_lengths[name] + (target_lengths[name] - current_lengths[name]) * ratio
            for name in self.context.cable_names
        }
        self.controller.apply_lengths(state, next_lengths)
