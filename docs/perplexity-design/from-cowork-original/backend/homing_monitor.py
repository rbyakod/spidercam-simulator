from __future__ import annotations
from threading import Lock

class HomingMonitor:
    def __init__(self):
        self._lock = Lock()
        self._state = {
            "axis_direction_ok": {"A": False, "B": False, "C": False, "D": False},
            "axis_homed": {"A": False, "B": False, "C": False, "D": False},
            "spool_radius_measured": False,
            "center_calibrated": False,
            "preload_ok": False,
            "bounds_verified": False,
            "path_square_ok": False,
            "path_circle_ok": False,
        }

    def mark_direction_ok(self, axis: str, ok: bool = True):
        with self._lock:
            self._state["axis_direction_ok"][axis] = ok

    def mark_homed(self, axis: str, homed: bool = True):
        with self._lock:
            self._state["axis_homed"][axis] = homed

    def mark_spool_radius(self, measured: bool = True):
        with self._lock:
            self._state["spool_radius_measured"] = measured

    def mark_center(self, ok: bool = True):
        with self._lock:
            self._state["center_calibrated"] = ok

    def mark_preload(self, ok: bool = True):
        with self._lock:
            self._state["preload_ok"] = ok

    def mark_bounds(self, ok: bool = True):
        with self._lock:
            self._state["bounds_verified"] = ok

    def mark_path(self, name: str, ok: bool = True):
        with self._lock:
            key = f"path_{name}_ok"
            if key in self._state:
                self._state[key] = ok

    def get(self) -> dict:
        with self._lock:
            return dict(self._state)
