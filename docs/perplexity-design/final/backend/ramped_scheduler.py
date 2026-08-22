from __future__ import annotations
import asyncio

class RampedScheduler:
    def __init__(self, target_hz: float = 50.0, ramp_steps: int = 50) -> None:
        self.target_hz = target_hz
        self.ramp_steps = ramp_steps
        self._tick = 0

    def _current_interval(self) -> float:
        if self._tick >= self.ramp_steps:
            return 1.0 / self.target_hz
        fraction = self._tick / self.ramp_steps
        slow = 1.0
        fast = 1.0 / self.target_hz
        return slow + (fast - slow) * fraction

    async def tick(self) -> None:
        await asyncio.sleep(self._current_interval())
        self._tick += 1
