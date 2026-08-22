from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
import time

class FaultCode(str, Enum):
    NONE = "NONE"
    CABLE_SLACK = "CABLE_SLACK"
    CABLE_OVERTENSION = "CABLE_OVERTENSION"
    LIMIT_TRIGGERED = "LIMIT_TRIGGERED"
    HOMING_FAILED = "HOMING_FAILED"
    MOTION_TIMEOUT = "MOTION_TIMEOUT"
    GPIO_ERROR = "GPIO_ERROR"
    COMM_ERROR = "COMM_ERROR"

@dataclass
class FaultEvent:
    code: FaultCode
    message: str
    timestamp: float = field(default_factory=time.time)
    axis: int = None

    def to_dict(self) -> dict:
        return {
            "code": self.code.value,
            "message": self.message,
            "timestamp": self.timestamp,
            "axis": self.axis,
        }

class FaultManager:
    def __init__(self) -> None:
        self._active = []
        self._history = []
        self.e_stop = False

    def raise_fault(self, code, message, axis=None):
        ev = FaultEvent(code=code, message=message, axis=axis)
        self._active.append(ev)
        self._history.append(ev)
        if code != FaultCode.NONE:
            self.e_stop = True
        return ev

    def clear(self) -> None:
        self._active.clear()
        self.e_stop = False

    def active(self) -> list:
        return [e.to_dict() for e in self._active]

    def history(self, n: int = 50) -> list:
        return [e.to_dict() for e in self._history[-n:]]

fault_manager = FaultManager()
