from __future__ import annotations
from homing import homing

class HomingMonitor:
    def __init__(self) -> None:
        self.enforce = True

    def check(self):
        if not self.enforce:
            return True, "Homing enforcement disabled"
        if not homing.all_homed:
            return False, "Machine not homed - run homing sequence first"
        return True, "Homed"

homing_monitor = HomingMonitor()
