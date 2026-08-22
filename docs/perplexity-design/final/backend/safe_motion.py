from __future__ import annotations
import numpy as np
from physics import check_tensions
from faults import fault_manager
from config import settings

class SafeMotionGuard:
    def validate(self, target: np.ndarray, payload_kg: float = 0.5):
        if fault_manager.e_stop:
            return False, "E-stop is active"
        W, H, D = settings.frame_width, settings.frame_height, settings.frame_depth
        margin = 0.05
        if not (margin <= target[0] <= W - margin and
                margin <= target[1] <= H - margin and
                margin <= target[2] <= D - margin):
            return False, f"Target {target.tolist()} is outside workspace"
        result = check_tensions(target, payload_kg)
        if not result["all_positive"]:
            return False, "Cable slack detected - tension below minimum"
        if not result["within_max"]:
            return False, "Cable overtension detected"
        return True, "OK"

safe_guard = SafeMotionGuard()
