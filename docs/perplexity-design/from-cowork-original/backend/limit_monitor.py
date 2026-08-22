from __future__ import annotations
import time

class LimitMonitor:
    def __init__(self, pi, switch_map: dict, on_limit):
        self.pi = pi
        self.switch_map = switch_map
        self.on_limit = on_limit
        self.callbacks = []
        self.last_hit = {}
        self.debounce_ms = 30
        try:
            import pigpio
            for axis, pin in self.switch_map.items():
                self.pi.set_mode(pin, pigpio.INPUT)
                self.pi.set_pull_up_down(pin, pigpio.PUD_UP)
                cb = self.pi.callback(pin, pigpio.EITHER_EDGE, self._make_cb(axis, pin))
                self.callbacks.append(cb)
        except Exception:
            pass  # sim mode

    def _make_cb(self, axis, pin):
        def cb(gpio, level, tick):
            now = time.time() * 1000
            prev = self.last_hit.get(axis, 0)
            if now - prev < self.debounce_ms:
                return
            self.last_hit[axis] = now
            state = self.pi.read(pin)
            triggered = (state == 0)
            self.on_limit(axis, triggered, tick)
        return cb

    def read_all(self):
        try:
            return {axis: self.pi.read(pin) == 0 for axis, pin in self.switch_map.items()}
        except Exception:
            return {axis: False for axis in self.switch_map}

    def close(self):
        for cb in self.callbacks:
            try:
                cb.cancel()
            except Exception:
                pass
        self.callbacks = []
