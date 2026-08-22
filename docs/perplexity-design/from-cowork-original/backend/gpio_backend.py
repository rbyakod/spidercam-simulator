from __future__ import annotations
from motion_backend import MotionBackend
from gpio_runtime import GPIORuntime
from limit_monitor import LimitMonitor

class GPIOMotionBackend(MotionBackend):
    def __init__(self, cfg, on_limit):
        self.runtime = GPIORuntime()
        self.monitor = LimitMonitor(
            self.runtime.pi,
            cfg.limit_switches,
            on_limit=on_limit
        )

    def mode(self) -> str:
        return "live"

    def move_step_deltas(self, deltas: dict[str, int]) -> None:
        self.runtime.move_step_deltas(deltas)

    def stop(self) -> None:
        self.runtime.stop()

    def read_switches(self) -> dict[str, bool]:
        return self.monitor.read_all()

    def close(self) -> None:
        self.monitor.close()
        self.runtime.close()
