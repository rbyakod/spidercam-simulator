from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from pydantic import BaseModel

from persistent_config import SystemConfig


class Target(BaseModel):
    x: float
    y: float
    z: float
    speed: float = 0.4


class PathCmd(BaseModel):
    name: str
    speed: float = 0.35
    size: float = 0.8
    radius: float = 0.45
    z: float = 0.9


@dataclass(frozen=True)
class RuntimeContext:
    config: SystemConfig
    anchors: Dict[str, Tuple[float, float, float]]
    bounds: Dict[str, Tuple[float, float]]
    spool_radius_m: float
    motor_steps_per_rev: int
    microsteps: int
    cable_names: Tuple[str, ...]


def build_runtime_context(config: SystemConfig) -> RuntimeContext:
    anchors = {
        name: tuple(float(value) for value in coords)
        for name, coords in config.frame.anchors.items()
    }
    bounds = {
        axis: tuple(float(value) for value in axis_range)
        for axis, axis_range in config.frame.bounds.items()
    }
    cable_names = tuple(sorted(anchors))
    return RuntimeContext(
        config=config,
        anchors=anchors,
        bounds=bounds,
        spool_radius_m=float(config.frame.spool_radius_m),
        motor_steps_per_rev=int(config.frame.motor_steps_per_rev),
        microsteps=int(config.motors.microsteps),
        cable_names=cable_names,
    )
