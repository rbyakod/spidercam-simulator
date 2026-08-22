from __future__ import annotations
from math import pi

class HardwareExecutor:
    def __init__(self, motion_backend, cfg_fn):
        self.motion_backend = motion_backend
        self.cfg_fn = cfg_fn

    def steps_from_length_delta(self, dl: float) -> int:
        cfg = self.cfg_fn()
        steps_per_rev = cfg.frame.motor_steps_per_rev
        microsteps = cfg.motors.microsteps
        radius = cfg.frame.spool_radius_m
        return int((dl / (2 * pi * radius)) * steps_per_rev * microsteps)

    def move_lengths(self, current_lengths: dict[str, float], next_lengths: dict[str, float]):
        deltas = {
            axis: self.steps_from_length_delta(next_lengths[axis] - current_lengths[axis])
            for axis in current_lengths
        }
        self.motion_backend.move_step_deltas(deltas)
        return deltas
