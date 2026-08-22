from __future__ import annotations
import asyncio
from faults import fault_manager, FaultCode

class LimitMonitor:
    def __init__(self, gpio_map=None) -> None:
        self._gpio_map = gpio_map or {}
        self._running = False

    def set_gpio_map(self, gpio_map: dict) -> None:
        self._gpio_map = gpio_map

    async def run(self) -> None:
        self._running = True
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            for pin in self._gpio_map.values():
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            while self._running:
                for axis, pin in self._gpio_map.items():
                    if GPIO.input(pin) == GPIO.LOW:
                        fault_manager.raise_fault(
                            FaultCode.LIMIT_TRIGGERED,
                            f"Limit switch triggered on axis {axis}",
                            axis=int(axis),
                        )
                await asyncio.sleep(0.01)
        except ImportError:
            while self._running:
                await asyncio.sleep(0.1)

    def stop(self) -> None:
        self._running = False

limit_monitor = LimitMonitor()
