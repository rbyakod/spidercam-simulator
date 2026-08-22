from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

class CalibrationStep(str, Enum):
    IDLE = "idle"
    HOMING = "homing"
    MOVE_TO_REF = "move_to_ref"
    MEASURE = "measure"
    COMPUTE = "compute"
    DONE = "done"
    FAILED = "failed"

@dataclass
class CalibrationState:
    step: CalibrationStep = CalibrationStep.IDLE
    step_index: int = 0
    total_steps: int = 5
    message: str = ""
    offsets: list = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    is_calibrated: bool = False

    def to_dict(self) -> dict:
        return {
            "step": self.step.value,
            "step_index": self.step_index,
            "total_steps": self.total_steps,
            "message": self.message,
            "offsets": self.offsets,
            "is_calibrated": self.is_calibrated,
        }

cal_state = CalibrationState()
