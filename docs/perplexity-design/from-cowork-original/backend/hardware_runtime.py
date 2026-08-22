from __future__ import annotations
import os

SIM_MODE = os.environ.get("SPIDERPI_SIM_GPIO", "1") == "1"

class HardwareRuntime:
    def __init__(self, switch_map: dict):
        self._sim_switches = {k: False for k in switch_map}
        self._sim_estop = False
        self.switch_map = switch_map
        self._real_pi = None
        if not SIM_MODE:
            try:
                import pigpio
                self._real_pi = pigpio.pi()
                if not self._real_pi.connected:
                    self._real_pi = None
            except Exception:
                pass

    def get_switch_states(self) -> dict[str, bool]:
        if self._real_pi:
            return {axis: self._real_pi.read(pin) == 0
                    for axis, pin in self.switch_map.items()}
        return dict(self._sim_switches)

    def get_estop_state(self) -> bool:
        if self._real_pi:
            try:
                return self._real_pi.read(24) == 0
            except Exception:
                return False
        return self._sim_estop

    def set_sim_switch(self, axis: str, triggered: bool):
        self._sim_switches[axis] = triggered

    def set_sim_estop(self, triggered: bool):
        self._sim_estop = triggered

    def close(self):
        if self._real_pi:
            self._real_pi.stop()
