from __future__ import annotations
import asyncio
import numpy as np

class SimExecutor:
    def __init__(self) -> None:
        self.step_counts = np.zeros(4, dtype=int)

    async def step_motors(self, delta_steps: np.ndarray) -> None:
        max_steps = int(np.max(np.abs(delta_steps)))
        if max_steps == 0:
            return
        await asyncio.sleep(max_steps * 0.0001)
        self.step_counts += delta_steps

    async def move_axis_until_limit(self, axis: int, speed: float) -> None:
        await asyncio.sleep(0.5)

    async def step_axis(self, axis: int, steps: int) -> None:
        await asyncio.sleep(abs(steps) * 0.0001)
        self.step_counts[axis] += steps

    def get_state(self) -> dict:
        return {"step_counts": self.step_counts.tolist(), "type": "simulation"}

sim_executor = SimExecutor()
