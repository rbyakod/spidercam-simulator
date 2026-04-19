from __future__ import annotations

from typing import Dict, Iterable, Tuple

from models import RuntimeContext


class BaseController:
    mode = "base"

    def __init__(self, context: RuntimeContext):
        self.context = context

    def is_ready(self, state: Dict[str, object]) -> Tuple[bool, list[str]]:
        return True, []

    def append_trace(self, state: Dict[str, object], message: str) -> None:
        trace = list(state.get("controller_trace", []))
        trace.append(message)
        state["controller_trace"] = trace[-50:]

    def _set_map(self, value: bool, names: Iterable[str]) -> Dict[str, bool]:
        return {name: value for name in names}

    def home(self, state: Dict[str, object]) -> Dict[str, object]:
        self.append_trace(state, f"{self.mode}: home")
        state["homed"] = self._set_map(True, self.context.cable_names)
        state["status"] = "idle"
        return {"ok": True}

    def verify_limits(self, state: Dict[str, object]) -> Dict[str, object]:
        self.append_trace(state, f"{self.mode}: verify_limits")
        state["limits_verified"] = True
        state["status"] = "idle"
        return {"ok": True}

    def verify_motor_directions(self, state: Dict[str, object]) -> Dict[str, object]:
        self.append_trace(state, f"{self.mode}: verify_motor_directions")
        state["motor_direction_ok"] = self._set_map(True, self.context.cable_names)
        state["status"] = "idle"
        return {"ok": True}

    def calibrate(self, state: Dict[str, object]) -> Dict[str, object]:
        self.append_trace(state, f"{self.mode}: calibrate")
        state["zero_lengths_m"] = {name: float(state["lengths"][name]) for name in self.context.cable_names}
        state["line_offsets_steps"] = {name: int(state["steps"][name]) for name in self.context.cable_names}
        state["status"] = "idle"
        return {"ok": True}
