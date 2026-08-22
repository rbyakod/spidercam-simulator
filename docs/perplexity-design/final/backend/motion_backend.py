from __future__ import annotations
import asyncio
import numpy as np
from physics import inverse_kinematics
from config import settings, steps_per_metre
from faults import fault_manager
from safe_motion import safe_guard
from planner import interpolate_path
from calibration import calibration

class MotionBackend:
    def __init__(self, executor=None) -> None:
        self.executor = executor
        self.current_pos = np.array([
            settings.frame_width / 2,
            settings.frame_height * 0.8,
            settings.frame_depth / 2,
        ])
        self.target_pos = self.current_pos.copy()
        self._moving = False
        self.spm = steps_per_metre()

    def set_executor(self, executor) -> None:
        self.executor = executor

    async def move_to(self, target: list, payload_kg: float = 0.5) -> dict:
        t = np.array(target, dtype=float)
        ok, reason = safe_guard.validate(t, payload_kg)
        if not ok:
            return {"success": False, "reason": reason}
        self._moving = True
        try:
            waypoints = [self.current_pos.tolist(), t.tolist()]
            traj = interpolate_path(waypoints)
            prev_lengths = inverse_kinematics(self.current_pos)
            if calibration.is_calibrated:
                prev_lengths = calibration.apply(prev_lengths)
            for pos in traj:
                if fault_manager.e_stop:
                    break
                new_lengths = inverse_kinematics(pos)
                if calibration.is_calibrated:
                    new_lengths = calibration.apply(new_lengths)
                delta_steps = ((new_lengths - prev_lengths) * self.spm).astype(int)
                if self.executor:
                    await self.executor.step_motors(delta_steps)
                self.current_pos = pos
                prev_lengths = new_lengths
                await asyncio.sleep(0.02)
            self.target_pos = t
            return {"success": True, "position": self.current_pos.tolist()}
        finally:
            self._moving = False

    def status(self) -> dict:
        return {
            "position": self.current_pos.tolist(),
            "target": self.target_pos.tolist(),
            "moving": self._moving,
            "cable_lengths": inverse_kinematics(self.current_pos).tolist(),
            "e_stop": fault_manager.e_stop,
        }

motion = MotionBackend()
