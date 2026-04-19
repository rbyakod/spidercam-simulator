from __future__ import annotations

from typing import Dict, List

from models import RuntimeContext


def clamp_target(context: RuntimeContext, x: float, y: float, z: float) -> Dict[str, float]:
    return {
        "x": max(context.bounds["x"][0], min(context.bounds["x"][1], x)),
        "y": max(context.bounds["y"][0], min(context.bounds["y"][1], y)),
        "z": max(context.bounds["z"][0], min(context.bounds["z"][1], z)),
    }


def validate_geometry(context: RuntimeContext) -> Dict[str, List[str] | bool]:
    issues: List[str] = []

    if len(context.cable_names) < 4:
        issues.append("insufficient_anchors")

    for axis, (low, high) in context.bounds.items():
        if low >= high:
            issues.append(f"invalid_bound_{axis}")

    for name, anchor in context.anchors.items():
        if len(anchor) != 3:
            issues.append(f"invalid_anchor_{name}")

    if context.spool_radius_m <= 0:
        issues.append("invalid_spool_radius")

    if context.motor_steps_per_rev <= 0:
        issues.append("invalid_motor_steps_per_rev")

    if context.microsteps <= 0:
        issues.append("invalid_microsteps")

    return {"valid": not issues, "issues": issues}
