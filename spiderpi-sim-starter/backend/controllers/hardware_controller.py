from __future__ import annotations

from typing import Dict, Tuple

from controllers.base_controller import BaseController


class HardwareController(BaseController):
    mode = "hardware"

    def is_ready(self, state: Dict[str, object]) -> Tuple[bool, list[str]]:
        reasons = ["hardware_controller_unavailable_in_starter"]
        return False, reasons

    def apply_lengths(self, state: Dict[str, object], next_lengths: Dict[str, float]) -> None:
        self.append_trace(state, "hardware: apply_lengths blocked")

    def home(self, state: Dict[str, object]) -> Dict[str, object]:
        self.append_trace(state, "hardware: home unavailable")
        return {"ok": False, "errors": ["hardware_controller_unavailable_in_starter"]}

    def verify_limits(self, state: Dict[str, object]) -> Dict[str, object]:
        self.append_trace(state, "hardware: verify_limits unavailable")
        return {"ok": False, "errors": ["hardware_controller_unavailable_in_starter"]}

    def verify_motor_directions(self, state: Dict[str, object]) -> Dict[str, object]:
        self.append_trace(state, "hardware: verify_motor_directions unavailable")
        return {"ok": False, "errors": ["hardware_controller_unavailable_in_starter"]}

    def calibrate(self, state: Dict[str, object]) -> Dict[str, object]:
        self.append_trace(state, "hardware: calibrate unavailable")
        return {"ok": False, "errors": ["hardware_controller_unavailable_in_starter"]}
