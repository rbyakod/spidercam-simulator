from __future__ import annotations

from typing import Dict, List

from kinematics import lengths_from_xyz
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


def validate_target(context: RuntimeContext, x: float, y: float, z: float) -> Dict[str, object]:
    errors: List[str] = []
    geometry = validate_geometry(context)
    if not geometry["valid"]:
        errors.extend(str(issue) for issue in geometry["issues"])

    if not (context.bounds["x"][0] <= x <= context.bounds["x"][1]):
        errors.append("target_out_of_bounds_x")
    if not (context.bounds["y"][0] <= y <= context.bounds["y"][1]):
        errors.append("target_out_of_bounds_y")
    if not (context.bounds["z"][0] <= z <= context.bounds["z"][1]):
        errors.append("target_out_of_bounds_z")

    lengths = lengths_from_xyz(context.anchors, x, y, z)
    for name, length in lengths.items():
        min_length, max_length = context.cable_length_limits[name]
        if length < min_length - 1e-6 or length > max_length + 1e-6:
            errors.append(f"cable_length_out_of_range_{name}")

    return {"valid": not errors, "errors": errors, "lengths": lengths}


def validate_position(context: RuntimeContext, position: Dict[str, float]) -> Dict[str, object]:
    return validate_target(
        context,
        float(position["x"]),
        float(position["y"]),
        float(position["z"]),
    )
