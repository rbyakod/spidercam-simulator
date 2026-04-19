from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from pydantic import BaseModel

from persistent_config import SystemConfig

SUPPORTED_MODES = ("sim", "dry_run", "hardware")


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


class ModeCmd(BaseModel):
    mode: str


@dataclass(frozen=True)
class RuntimeContext:
    config: SystemConfig
    anchors: Dict[str, Tuple[float, float, float]]
    bounds: Dict[str, Tuple[float, float]]
    spool_radius_m: float
    motor_steps_per_rev: int
    microsteps: int
    cable_names: Tuple[str, ...]
    cable_length_limits: Dict[str, Tuple[float, float]]
    default_mode: str


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
    x_bounds = bounds["x"]
    y_bounds = bounds["y"]
    z_bounds = bounds["z"]
    corners = [(x, y, z) for x in x_bounds for y in y_bounds for z in z_bounds]
    cable_length_limits = {}
    for name, (ax, ay, az) in anchors.items():
        lengths = [
            ((x - ax) ** 2 + (y - ay) ** 2 + (z - az) ** 2) ** 0.5
            for x, y, z in corners
        ]
        cable_length_limits[name] = (min(lengths), max(lengths))
    default_mode = str(getattr(config, "controller_mode_default", "sim"))
    if default_mode not in SUPPORTED_MODES:
        default_mode = "sim"
    return RuntimeContext(
        config=config,
        anchors=anchors,
        bounds=bounds,
        spool_radius_m=float(config.frame.spool_radius_m),
        motor_steps_per_rev=int(config.frame.motor_steps_per_rev),
        microsteps=int(config.motors.microsteps),
        cable_names=cable_names,
        cable_length_limits=cable_length_limits,
        default_mode=default_mode,
    )
