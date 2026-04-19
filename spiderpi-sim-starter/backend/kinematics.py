from __future__ import annotations

from math import pi, sqrt
from typing import Dict, Mapping, Sequence

from models import RuntimeContext


def lengths_from_xyz(
    anchors: Mapping[str, Sequence[float]],
    x: float,
    y: float,
    z: float,
) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for name, (ax, ay, az) in anchors.items():
        out[name] = sqrt((x - ax) ** 2 + (y - ay) ** 2 + (z - az) ** 2)
    return out


def lengths_from_position(context: RuntimeContext, position: Mapping[str, float]) -> Dict[str, float]:
    return lengths_from_xyz(
        context.anchors,
        float(position["x"]),
        float(position["y"]),
        float(position["z"]),
    )


def steps_from_delta_length(delta_len: float, context: RuntimeContext) -> int:
    if context.spool_radius_m <= 0:
        return 0
    revs = delta_len / (2 * pi * context.spool_radius_m)
    return int(revs * context.motor_steps_per_rev * context.microsteps)
