from __future__ import annotations
from persistent_config import load_config
from ramped_scheduler import MultiAxisRampScheduler

class GPIORuntime:
    def __init__(self):
        import pigpio
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpiod not running")
        self.scheduler = None
        self.cfg = None
        self.reload()

    def reload(self):
        cfg = load_config()
        gpio_map = {
            axis: {
                "step": pins.step,
                "dir": pins.dir,
                "en": pins.en,
                "invert_dir": pins.invert_dir,
            }
            for axis, pins in cfg.gpio_map.items()
        }
        self.scheduler = MultiAxisRampScheduler(self.pi, gpio_map)
        self.cfg = cfg

    def move_step_deltas(self, deltas: dict[str, int]):
        mt = self.cfg.motors
        self.scheduler.run_blocking(
            deltas,
            v_start=mt.start_freq_hz,
            v_max=mt.max_freq_hz,
            accel_steps_s2=mt.accel_steps_s2,
        )

    def stop(self):
        self.scheduler.stop()

    def read_pin(self, pin: int) -> int:
        return self.pi.read(pin)

    def close(self):
        self.scheduler.stop()
        self.pi.stop()
