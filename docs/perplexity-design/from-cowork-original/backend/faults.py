from __future__ import annotations
from dataclasses import dataclass, asdict
from threading import Lock
import time

@dataclass
class FaultRecord:
    active: bool = False
    code: str | None = None
    message: str | None = None
    axis: str | None = None
    ts: float | None = None
    level: str = "error"

class FaultManager:
    def __init__(self):
        self._lock = Lock()
        self._fault = FaultRecord()
        self._history: list[dict] = []

    def set_fault(self, code: str, message: str, axis: str | None = None, level: str = "error"):
        with self._lock:
            self._fault = FaultRecord(
                active=True, code=code, message=message,
                axis=axis, ts=time.time(), level=level
            )
            self._history.append(asdict(self._fault))
            self._history = self._history[-200:]

    def clear(self):
        with self._lock:
            self._fault = FaultRecord()

    def get(self):
        with self._lock:
            return asdict(self._fault)

    def history(self):
        with self._lock:
            return list(self._history)

    def active(self) -> bool:
        with self._lock:
            return self._fault.active
