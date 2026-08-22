from __future__ import annotations
import asyncio
import numpy as np
from config import settings
from faults import fault_manager, FaultCode

class HomingController:
    HOMING_SPEED = 0.05
    BACKOFF_STEPS = 100

    def __init__(self) -> None:
        self.homed = [False, False, False, False]
        self.zero_offsets = np.zeros(4)

    @property
    def all_homed(self) -> bool:
        return all(self.homed)

    async def home_axis(self, axis: int, executor) -> bool:
        try:
            await executor.move_axis_until_limit(axis, self.HOMING_SPEED)
            await executor.step_axis(axis, -self.BACKOFF_STEPS)
            self.homed[axis] = True
            return True
        except Exception as exc:
            fault_manager.raise_fault(
                FaultCode.HOMING_FAILED,
                f"Homing failed on axis {axis}: {exc}",
                axis=axis,
            )
            return False

    async def home_all(self, executor) -> bool:
        self.homed = [False, False, False, False]
        for axis in range(4):
            ok = await self.home_axis(axis, executor)
            if not ok:
                return False
        return True

    def to_dict(self) -> dict:
        return {
            "homed": self.homed,
            "all_homed": self.all_homed,
            "zero_offsets": self.zero_offsets.tolist(),
        }

homing = HomingController()
