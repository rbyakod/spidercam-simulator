from __future__ import annotations
from motion_backend import MotionBackend

class SimMotionBackend(MotionBackend):
    def __init__(self):
        self._switches = {"A": False, "B": False, "C": False, "D": False}
        self.last_deltas = {"A": 0, "B": 0, "C": 0, "D": 0}

    def mode(self) -> str:
        return "sim"

    def move_step_deltas(self, deltas: dict[str, int]) -> None:
        self.last_deltas = deltas

    def stop(self) -> None:
        self.last_deltas = {"A": 0, "B": 0, "C": 0, "D": 0}

    def read_switches(self) -> dict[str, bool]:
        return self._switches

    def close(self) -> None:
        pass
