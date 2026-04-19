from __future__ import annotations

import time
from typing import Dict, Iterable, List

from kinematics import lengths_from_position
from models import RuntimeContext
from workspace import clamp_target, validate_geometry

DERIVED_WARNING_KEYS = {
    "calibration_incomplete",
    "homing_incomplete",
    "motor_direction_unverified",
    "limits_unverified",
}


def _ordered_bool_map(source: Dict[str, bool], names: Iterable[str]) -> Dict[str, bool]:
    return {name: bool(source.get(name, False)) for name in names}


def _calibration_valid(context: RuntimeContext) -> bool:
    calibration = context.config.calibration
    return (
        all(calibration.homed.get(name, False) for name in context.cable_names)
        and all(calibration.motor_direction_ok.get(name, False) for name in context.cable_names)
        and calibration.limits_verified
    )


def _calibration_warnings(context: RuntimeContext) -> List[str]:
    calibration = context.config.calibration
    warnings: List[str] = []
    if not _calibration_valid(context):
        warnings.append("calibration_incomplete")
    if not all(calibration.homed.get(name, False) for name in context.cable_names):
        warnings.append("homing_incomplete")
    if not all(calibration.motor_direction_ok.get(name, False) for name in context.cable_names):
        warnings.append("motor_direction_unverified")
    if not calibration.limits_verified:
        warnings.append("limits_unverified")
    return warnings


def _default_position(context: RuntimeContext) -> Dict[str, float]:
    return clamp_target(context, 1.0, 1.0, 0.9)


def default_state(context: RuntimeContext) -> Dict[str, object]:
    geometry = validate_geometry(context)
    position = _default_position(context)
    existing_faults: List[str] = []
    if not geometry["valid"]:
        existing_faults.append("invalid_geometry")

    state: Dict[str, object] = {
        "mode": "sim",
        "status": "idle",
        "estop": False,
        "armed": True,
        "controller_ready": bool(geometry["valid"]),
        "geometry_valid": bool(geometry["valid"]),
        "calibration_valid": _calibration_valid(context),
        "faults": existing_faults,
        "warnings": _calibration_warnings(context),
        "homed": _ordered_bool_map(context.config.calibration.homed, context.cable_names),
        "position": position,
        "target": dict(position),
        "speed": 0.4,
        "anchors": {name: list(coords) for name, coords in context.anchors.items()},
        "bounds": {axis: list(axis_range) for axis, axis_range in context.bounds.items()},
        "lengths": lengths_from_position(context, position),
        "steps": {name: 0 for name in context.cable_names},
        "spools": {name: 0.0 for name in context.cable_names},
        "trail": [],
        "path": {"name": None, "index": 0, "points": []},
        "updated_at": time.time(),
    }
    return state


def refresh_state(raw_state: Dict[str, object], context: RuntimeContext) -> Dict[str, object]:
    geometry = validate_geometry(context)
    state = dict(raw_state)

    position = state.get("position")
    if not isinstance(position, dict):
        position = _default_position(context)
    position = clamp_target(
        context,
        float(position.get("x", 1.0)),
        float(position.get("y", 1.0)),
        float(position.get("z", 0.9)),
    )

    target = state.get("target")
    if not isinstance(target, dict):
        target = dict(position)
    target = clamp_target(
        context,
        float(target.get("x", position["x"])),
        float(target.get("y", position["y"])),
        float(target.get("z", position["z"])),
    )

    step_state = state.get("steps") if isinstance(state.get("steps"), dict) else {}
    spool_state = state.get("spools") if isinstance(state.get("spools"), dict) else {}
    path_state = state.get("path") if isinstance(state.get("path"), dict) else {}

    faults = [fault for fault in state.get("faults", []) if fault != "invalid_geometry"]
    if not geometry["valid"]:
        faults.append("invalid_geometry")

    warnings = [warning for warning in state.get("warnings", []) if warning not in DERIVED_WARNING_KEYS]
    warnings.extend(_calibration_warnings(context))

    normalized = {
        "mode": str(state.get("mode", "sim")),
        "status": "estopped" if state.get("estop") else str(state.get("status", "idle")),
        "estop": bool(state.get("estop", False)),
        "armed": bool(state.get("armed", True)),
        "controller_ready": bool(state.get("controller_ready", True)) and bool(geometry["valid"]),
        "geometry_valid": bool(geometry["valid"]),
        "calibration_valid": _calibration_valid(context),
        "faults": faults,
        "warnings": warnings,
        "homed": _ordered_bool_map(context.config.calibration.homed, context.cable_names),
        "position": position,
        "target": target,
        "speed": float(state.get("speed", 0.4)),
        "anchors": {name: list(coords) for name, coords in context.anchors.items()},
        "bounds": {axis: list(axis_range) for axis, axis_range in context.bounds.items()},
        "lengths": lengths_from_position(context, position),
        "steps": {name: int(step_state.get(name, 0)) for name in context.cable_names},
        "spools": {name: float(spool_state.get(name, 0.0)) for name in context.cable_names},
        "trail": list(state.get("trail", []))[-250:],
        "path": {
            "name": path_state.get("name"),
            "index": int(path_state.get("index", 0)),
            "points": list(path_state.get("points", [])),
        },
        "updated_at": float(state.get("updated_at", time.time())),
    }
    return normalized
