from __future__ import annotations
import time

class HomingController:
    def __init__(self, runtime, switch_state_fn, fault_mgr, on_status):
        self.runtime = runtime
        self.switch_state_fn = switch_state_fn
        self.fault_mgr = fault_mgr
        self.on_status = on_status

    def home_axis(self, axis: str, seek_steps=2400, backoff_steps=300,
                  slow_seek_steps=400, timeout_s=30.0):
        self.on_status(f"homing:{axis}:seek")
        if self.switch_state_fn().get(axis, False):
            self.runtime.move_step_deltas({axis: backoff_steps})
            if self.switch_state_fn().get(axis, False):
                self.fault_mgr.set_fault("HOME_SWITCH_STUCK", f"{axis} switch stuck active")
                return False
        self.runtime.move_step_deltas({axis: -abs(seek_steps)})
        if not self.switch_state_fn().get(axis, False):
            self.fault_mgr.set_fault("HOME_NOT_FOUND", f"{axis} switch not found")
            return False
        self.on_status(f"homing:{axis}:backoff")
        self.runtime.move_step_deltas({axis: abs(backoff_steps)})
        if self.switch_state_fn().get(axis, False):
            self.fault_mgr.set_fault("HOME_BACKOFF_FAIL", f"{axis} switch still active")
            return False
        self.on_status(f"homing:{axis}:slow")
        self.runtime.move_step_deltas({axis: -abs(slow_seek_steps)})
        if not self.switch_state_fn().get(axis, False):
            self.fault_mgr.set_fault("HOME_SLOW_NOT_FOUND", f"{axis} switch not found on slow approach")
            return False
        self.on_status(f"homing:{axis}:done")
        return True

    def home_all(self, axes=("A", "B", "C", "D")):
        out = {}
        for axis in axes:
            if self.fault_mgr.active():
                out[axis] = False
                continue
            out[axis] = self.home_axis(axis)
        return out
