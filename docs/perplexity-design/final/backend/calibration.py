from __future__ import annotations
import numpy as np
from physics import cable_lengths
from config import settings

class CalibrationManager:
    def __init__(self) -> None:
        self.offsets = np.zeros(4)
        self.is_calibrated = False
        self._ref_pos = np.array([
            settings.frame_width / 2,
            settings.frame_height / 2,
            settings.frame_depth / 2,
        ])

    def compute_offsets(self, measured_lengths: list) -> np.ndarray:
        ideal = cable_lengths(self._ref_pos)
        measured = np.array(measured_lengths)
        self.offsets = measured - ideal
        self.is_calibrated = True
        return self.offsets

    def apply(self, raw_lengths: np.ndarray) -> np.ndarray:
        return raw_lengths - self.offsets

    def to_dict(self) -> dict:
        return {
            "is_calibrated": self.is_calibrated,
            "offsets": self.offsets.tolist(),
            "ref_pos": self._ref_pos.tolist(),
        }

    def from_dict(self, d: dict) -> None:
        self.offsets = np.array(d.get("offsets", [0.0, 0.0, 0.0, 0.0]))
        self.is_calibrated = d.get("is_calibrated", False)

calibration = CalibrationManager()
