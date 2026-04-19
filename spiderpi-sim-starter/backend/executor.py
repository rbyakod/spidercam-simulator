from __future__ import annotations

from math import sqrt
from typing import Dict

from controllers.controller_manager import ControllerManager
from models import RuntimeContext, SUPPORTED_MODES
from workspace import validate_target


class MotionExecutor:
    def __init__(self, context: RuntimeContext, controller_manager: ControllerManager):
        self.context = context
        self.controller_manager = controller_manager

    def _controller(self, state: Dict[str, object]):
        return self.controller_manager.get(str(state.get("mode", self.context.default_mode)))

    def _set_last_error(self, state: Dict[str, object], errors: list[str]) -> Dict[str, object]:
        state["last_error"] = ", ".join(errors)
        return {"ok": False, "errors": errors}

    def _clear_last_error(self, state: Dict[str, object]) -> None:
        state["last_error"] = None

    def _set_current_as_target(self, state: Dict[str, object]) -> None:
        state["target"] = dict(state["position"])
        state["target_lengths"] = dict(state["lengths"])

    def sync_state(self, state: Dict[str, object]) -> Dict[str, object]:
        controller = self._controller(state)
        ready, reasons = controller.is_ready(state)
        state["controller_ready"] = bool(ready) and bool(state.get("geometry_valid", True))
        state["controller_detail"] = ", ".join(reasons) if reasons else None
        return {"ok": True}

    def _motion_preconditions(self, state: Dict[str, object]) -> list[str]:
        self.sync_state(state)
        errors: list[str] = []
        if state.get("estop"):
            errors.append("estopped")
        if not state.get("armed", False):
            errors.append("not_armed")
        if not state.get("controller_ready", False):
            detail = state.get("controller_detail")
            errors.append(str(detail or "controller_not_ready"))
        if not all(bool(value) for value in state.get("homed", {}).values()):
            errors.append("not_homed")
        if not bool(state.get("limits_verified", False)):
            errors.append("limits_unverified")
        if not all(bool(value) for value in state.get("motor_direction_ok", {}).values()):
            errors.append("motor_direction_unverified")
        if not bool(state.get("calibration_valid", False)):
            errors.append("calibration_invalid")
        return errors

    def set_mode(self, state: Dict[str, object], mode: str) -> Dict[str, object]:
        if mode not in SUPPORTED_MODES:
            return self._set_last_error(state, ["unsupported_mode"])
        self.stop(state)
        state["mode"] = mode
        self.sync_state(state)
        return {"ok": True}

    def arm(self, state: Dict[str, object]) -> Dict[str, object]:
        state["armed"] = True
        self._clear_last_error(state)
        self.sync_state(state)
        return {"ok": True}

    def disarm(self, state: Dict[str, object]) -> Dict[str, object]:
        self.stop(state)
        state["armed"] = False
        self.sync_state(state)
        return {"ok": True}

    def home(self, state: Dict[str, object]) -> Dict[str, object]:
        if state.get("estop"):
            return self._set_last_error(state, ["estopped"])
        state["status"] = "homing"
        result = self._controller(state).home(state)
        self._set_current_as_target(state)
        self.sync_state(state)
        if not result.get("ok", False):
            state["status"] = "idle"
            return self._set_last_error(state, list(result.get("errors", ["home_failed"])))
        self._clear_last_error(state)
        return result

    def verify_limits(self, state: Dict[str, object]) -> Dict[str, object]:
        if state.get("estop"):
            return self._set_last_error(state, ["estopped"])
        result = self._controller(state).verify_limits(state)
        self.sync_state(state)
        if not result.get("ok", False):
            return self._set_last_error(state, list(result.get("errors", ["verify_limits_failed"])))
        self._clear_last_error(state)
        return result

    def verify_motor_directions(self, state: Dict[str, object]) -> Dict[str, object]:
        if state.get("estop"):
            return self._set_last_error(state, ["estopped"])
        result = self._controller(state).verify_motor_directions(state)
        self.sync_state(state)
        if not result.get("ok", False):
            return self._set_last_error(state, list(result.get("errors", ["verify_motor_directions_failed"])))
        self._clear_last_error(state)
        return result

    def calibrate(self, state: Dict[str, object]) -> Dict[str, object]:
        if state.get("estop"):
            return self._set_last_error(state, ["estopped"])
        if not all(bool(value) for value in state.get("homed", {}).values()):
            return self._set_last_error(state, ["not_homed"])
        state["status"] = "calibrating"
        result = self._controller(state).calibrate(state)
        self.sync_state(state)
        if not result.get("ok", False):
            state["status"] = "idle"
            return self._set_last_error(state, list(result.get("errors", ["calibration_failed"])))
        self._clear_last_error(state)
        return result

    def set_target(self, state: Dict[str, object], x: float, y: float, z: float, speed: float) -> Dict[str, object]:
        precondition_errors = self._motion_preconditions(state)
        if precondition_errors:
            return self._set_last_error(state, precondition_errors)

        validation = validate_target(self.context, x, y, z)
        if not validation["valid"]:
            return self._set_last_error(state, validation["errors"])

        self._clear_last_error(state)
        state["target"] = {"x": float(x), "y": float(y), "z": float(z)}
        state["target_lengths"] = dict(validation["lengths"])
        state["workspace_valid"] = True
        state["speed"] = max(0.05, min(speed, 1.0))
        state["status"] = "moving"
        return {"ok": True}

    def clear_path(self, state: Dict[str, object]) -> None:
        state["path"] = {"name": None, "index": 0, "points": []}

    def queue_path(self, state: Dict[str, object], name: str, points, speed: float) -> Dict[str, object]:
        precondition_errors = self._motion_preconditions(state)
        if precondition_errors:
            return self._set_last_error(state, precondition_errors)

        for index, point in enumerate(points):
            validation = validate_target(self.context, point["x"], point["y"], point["z"])
            if not validation["valid"]:
                errors = [f"path_point_{index}:{error}" for error in validation["errors"]]
                return self._set_last_error(state, errors)

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

    def reset_estop(self, state: Dict[str, object]) -> Dict[str, object]:
        state["estop"] = False
        self._clear_last_error(state)
        self.sync_state(state)
        state["status"] = "idle"
        return {"ok": True}

    def advance_state(self, state: Dict[str, object], dt: float) -> None:
        self.sync_state(state)
        if state["estop"]:
            state["status"] = "estopped"
            return
        if state["status"] not in {"moving"}:
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
        self._controller(state).apply_lengths(state, next_lengths)
