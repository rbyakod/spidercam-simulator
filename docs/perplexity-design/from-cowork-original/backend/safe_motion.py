from __future__ import annotations
import time

class SafeMotionController:
    def __init__(self, runtime, fault_mgr, state_ref, cfg_fn):
        self.runtime = runtime
        self.fault_mgr = fault_mgr
        self.state_ref = state_ref
        self.cfg_fn = cfg_fn
        self.motion_active = False
        self.abort_requested = False

    def request_abort(self, code="ABORT", message="Motion aborted", axis=None):
        self.abort_requested = True
        self.runtime.stop()
        self.fault_mgr.set_fault(code, message, axis=axis)

    def clear_abort(self):
        self.abort_requested = False

    def check_soft_bounds(self, x, y, z):
        b = self.cfg_fn().frame.bounds
        return (b["x"][0] <= x <= b["x"][1] and
                b["y"][0] <= y <= b["y"][1] and
                b["z"][0] <= z <= b["z"][1])

    def execute_step_move(self, deltas: dict[str, int], watchdog_s=10.0):
        if self.fault_mgr.active():
            raise RuntimeError("Fault active")
        self.motion_active = True
        self.abort_requested = False
        started = time.time()
        try:
            self.runtime.move_step_deltas(deltas)
            if time.time() - started > watchdog_s:
                self.request_abort("WATCHDOG_TIMEOUT", "Motion exceeded watchdog time")
        finally:
            self.motion_active = False
