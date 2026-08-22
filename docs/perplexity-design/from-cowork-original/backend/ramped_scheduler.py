from __future__ import annotations
from motion_profile import dda_sync_plan

class MultiAxisRampScheduler:
    def __init__(self, pi, gpio_map: dict):
        self.pi = pi
        self.gpio_map = gpio_map
        self.wave_ids = []
        try:
            import pigpio
            for cfg in gpio_map.values():
                self.pi.set_mode(cfg["step"], pigpio.OUTPUT)
                self.pi.set_mode(cfg["dir"], pigpio.OUTPUT)
                if cfg.get("en") is not None:
                    self.pi.set_mode(cfg["en"], pigpio.OUTPUT)
                    self.pi.write(cfg["en"], 0)
        except Exception:
            pass

    def clear_waves(self):
        try:
            self.pi.wave_tx_stop()
            for wid in self.wave_ids:
                try:
                    self.pi.wave_delete(wid)
                except Exception:
                    pass
            self.wave_ids = []
            self.pi.wave_clear()
        except Exception:
            pass

    def set_dirs(self, deltas: dict[str, int]):
        try:
            for axis, steps in deltas.items():
                inv = bool(self.gpio_map[axis].get("invert_dir", False))
                direction = 1 if steps >= 0 else 0
                if inv:
                    direction = 1 - direction
                self.pi.write(self.gpio_map[axis]["dir"], direction)
        except Exception:
            pass

    def run_blocking(self, deltas: dict[str, int], v_start=250, v_max=2200, accel_steps_s2=7000):
        self.clear_waves()
        self.set_dirs(deltas)
        try:
            import pigpio
            schedule = dda_sync_plan(deltas, v_start=v_start, v_max=v_max, accel_steps_s2=accel_steps_s2)
            chain = []
            for block in schedule:
                freq = max(1, int(block["freq_hz"]))
                half_us = max(2, int(500000 / freq))
                pulses = []
                for pulse_mask in block["pulses"]:
                    on_mask = 0
                    for axis, step_dir in pulse_mask.items():
                        if step_dir != 0:
                            on_mask |= 1 << self.gpio_map[axis]["step"]
                    if on_mask == 0:
                        pulses.append(pigpio.pulse(0, 0, half_us * 2))
                    else:
                        pulses.append(pigpio.pulse(on_mask, 0, half_us))
                        pulses.append(pigpio.pulse(0, on_mask, half_us))
                self.pi.wave_add_generic(pulses)
                wid = self.pi.wave_create()
                self.wave_ids.append(wid)
                chain += [255, 0, wid, 255, 1, 1, 0]
            self.pi.wave_chain(chain)
            while self.pi.wave_tx_busy():
                pass
        except Exception:
            pass
        self.clear_waves()

    def stop(self):
        self.clear_waves()
