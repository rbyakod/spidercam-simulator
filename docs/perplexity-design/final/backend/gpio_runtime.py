from __future__ import annotations
import asyncio
import numpy as np

STEP_PULSE_US = 10

class GPIORuntime:
    def __init__(self, gpio_map: dict) -> None:
        self.gpio_map = gpio_map
        self._gpio = None

    def _setup(self) -> None:
        import RPi.GPIO as GPIO
        self._gpio = GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for axis_conf in self.gpio_map.get("axes", []):
            GPIO.setup(axis_conf["step_pin"], GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(axis_conf["dir_pin"],  GPIO.OUT, initial=GPIO.LOW)
            if "enable_pin" in axis_conf:
                GPIO.setup(axis_conf["enable_pin"], GPIO.OUT, initial=GPIO.HIGH)

    def _enable(self, enable: bool) -> None:
        import RPi.GPIO as GPIO
        for axis_conf in self.gpio_map.get("axes", []):
            if "enable_pin" in axis_conf:
                GPIO.output(axis_conf["enable_pin"], GPIO.LOW if enable else GPIO.HIGH)

    def _pulse_axis(self, axis_idx: int, steps: int) -> None:
        import RPi.GPIO as GPIO
        import time
        if axis_idx >= len(self.gpio_map.get("axes", [])):
            return
        conf = self.gpio_map["axes"][axis_idx]
        step_pin = conf["step_pin"]
        dir_pin  = conf["dir_pin"]
        direction = GPIO.HIGH if steps >= 0 else GPIO.LOW
        GPIO.output(dir_pin, direction)
        for _ in range(abs(steps)):
            GPIO.output(step_pin, GPIO.HIGH)
            time.sleep(STEP_PULSE_US / 1e6)
            GPIO.output(step_pin, GPIO.LOW)
            time.sleep(STEP_PULSE_US / 1e6)

    async def step_motors(self, delta_steps: np.ndarray) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._step_motors_sync, delta_steps)

    def _step_motors_sync(self, delta_steps: np.ndarray) -> None:
        for i, steps in enumerate(delta_steps):
            if steps != 0:
                self._pulse_axis(i, int(steps))

    async def move_axis_until_limit(self, axis: int, speed: float) -> None:
        import RPi.GPIO as GPIO
        pins = self.gpio_map.get("limit_pins", [])
        limit_pin = pins[axis] if axis < len(pins) else None
        if limit_pin is None:
            await asyncio.sleep(2.0)
            return
        GPIO.setup(limit_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        while GPIO.input(limit_pin) == GPIO.HIGH:
            self._pulse_axis(axis, 1)
            await asyncio.sleep(0.001)

    async def step_axis(self, axis: int, steps: int) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._pulse_axis, axis, steps)

    def cleanup(self) -> None:
        if self._gpio:
            self._gpio.cleanup()

    def get_state(self) -> dict:
        return {"type": "gpio_hardware"}
