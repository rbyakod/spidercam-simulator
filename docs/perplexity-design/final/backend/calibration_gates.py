from __future__ import annotations
from calibration import calibration
from faults import fault_manager

def require_calibration():
    if not calibration.is_calibrated:
        return False, "System not calibrated - run calibration wizard first"
    if fault_manager.e_stop:
        return False, "E-stop active - clear faults before proceeding"
    return True, "OK"
