from __future__ import annotations

import time
from typing import Dict, Iterable, List

from models import RuntimeContext, SUPPORTED_MODES
from workspace import clamp_target, validate_geometry, validate_position, validate_target

DERIVED_WARNING_KEYS = {
    "calibration_incomplete",
    "homing_incomplete",
    "motor_direction_unverified",
    "limits_unverified",
    "workspace_invalid",
    "target_invalid",
    "controller_not_ready",
}


def _default_mode(context: RuntimeContext) -> str:
    return context.default_mode if context.default_mode in SUPPORTED_MODES else "sim"


def _ordered_bool_map(source: Dict[str, bool], names: Iterable[str], default_value: bool = False) -> Dict[str, bool]:
    return {name: bool(source.get(name, default_value)) for name in names}


def _ordered_float_map(source: Dict[str, float], names: Iterable[str], default_map: Dict[str, float]) -> Dict[str, float]:
    return {name: float(source.get(name, default_map[name])) for name in names}


def _ordered_int_map(source: Dict[str, int], names: Iterable[str], default_map: Dict[str, int]) -> Dict[str, int]:
    return {name: int(source.get(name, default_map[name])) for name in names}


def _default_position(context: RuntimeContext) -> Dict[str, float]:
    return clamp_target(context, 1.0, 1.0, 0.9)


def _normalize_pose(raw_pose: object, default_pose: Dict[str, float]) -> Dict[str, float]:
    if not isinstance(raw_pose, dict):
        return dict(default_pose)
    return {
        "x": float(raw_pose.get("x", default_pose["x"])),
        "y": float(raw_pose.get("y", default_pose["y"])),
        "z": float(raw_pose.get("z", default_pose["z"])),
    }


def _normalize_lengths(raw_lengths: object, default_lengths: Dict[str, float], names: Iterable[str]) -> Dict[str, float]:
    if not isinstance(raw_lengths, dict):
        return dict(default_lengths)
    return {
        name: float(raw_lengths.get(name, default_lengths[name]))
        for name in names
    }


def _calibration_defaults(context: RuntimeContext, mode: str, position_lengths: Dict[str, float], legacy_sim_state: bool) -> Dict[str, object]:
    sim_ready = mode == "sim" and legacy_sim_state
    if sim_ready:
        return {
            "homed": {name: True for name in context.cable_names},
            "limits_verified": True,
            "motor_direction_ok": {name: True for name in context.cable_names},
            "zero_lengths_m": {name: float(position_lengths[name]) for name in context.cable_names},
            "line_offsets_steps": {name: 0 for name in context.cable_names},
        }
    return {
        "homed": _ordered_bool_map(context.config.calibration.homed, context.cable_names, False),
        "limits_verified": bool(context.config.calibration.limits_verified),
        "motor_direction_ok": _ordered_bool_map(context.config.calibration.motor_direction_ok, context.cable_names, False),
        "zero_lengths_m": _ordered_float_map(context.config.calibration.zero_lengths_m, context.cable_names, {name: 0.0 for name in context.cable_names}),
        "line_offsets_steps": _ordered_int_map(context.config.calibration.line_offsets_steps, context.cable_names, {name: 0 for name in context.cable_names}),
    }


def _calibration_valid(homed: Dict[str, bool], motor_direction_ok: Dict[str, bool], limits_verified: bool) -> bool:
    return (
        all(homed.values())
        and all(motor_direction_ok.values())
        and bool(limits_verified)
    )


def _calibration_warnings(homed: Dict[str, bool], motor_direction_ok: Dict[str, bool], limits_verified: bool) -> List[str]:
    warnings: List[str] = []
    if not _calibration_valid(homed, motor_direction_ok, limits_verified):
        warnings.append("calibration_incomplete")
    if not all(homed.values()):
        warnings.append("homing_incomplete")
    if not all(motor_direction_ok.values()):
        warnings.append("motor_direction_unverified")
    if not limits_verified:
        warnings.append("limits_unverified")
    return warnings


def default_state(context: RuntimeContext) -> Dict[str, object]:
    geometry = validate_geometry(context)
    mode = _default_mode(context)
    position = _default_position(context)
    position_validation = validate_position(context, position)
    calibration_defaults = _calibration_defaults(context, mode, position_validation["lengths"], legacy_sim_state=True)
    existing_faults: List[str] = []
    if not geometry["valid"]:
        existing_faults.append("invalid_geometry")

    homed = calibration_defaults["homed"]
    motor_direction_ok = calibration_defaults["motor_direction_ok"]
    limits_verified = bool(calibration_defaults["limits_verified"])

    return {
        "mode": mode,
        "status": "idle",
        "estop": False,
        "armed": True,
        "controller_ready": mode == "sim" and bool(geometry["valid"]),
        "controller_detail": None,
        "geometry_valid": bool(geometry["valid"]),
        "workspace_valid": bool(position_validation["valid"]),
        "calibration_valid": _calibration_valid(homed, motor_direction_ok, limits_verified),
        "faults": existing_faults,
        "warnings": _calibration_warnings(homed, motor_direction_ok, limits_verified),
        "last_error": None,
        "homed": homed,
        "limits_verified": limits_verified,
        "motor_direction_ok": motor_direction_ok,
        "zero_lengths_m": calibration_defaults["zero_lengths_m"],
        "line_offsets_steps": calibration_defaults["line_offsets_steps"],
        "controller_trace": [],
        "position": position,
        "target": dict(position),
        "speed": 0.4,
        "anchors": {name: list(coords) for name, coords in context.anchors.items()},
        "bounds": {axis: list(axis_range) for axis, axis_range in context.bounds.items()},
        "lengths": dict(position_validation["lengths"]),
        "target_lengths": dict(position_validation["lengths"]),
        "steps": {name: 0 for name in context.cable_names},
        "spools": {name: 0.0 for name in context.cable_names},
        "trail": [],
        "path": {"name": None, "index": 0, "points": []},
        "updated_at": time.time(),
    }


def refresh_state(raw_state: Dict[str, object], context: RuntimeContext) -> Dict[str, object]:
    geometry = validate_geometry(context)
    state = dict(raw_state)
    mode = str(state.get("mode", _default_mode(context)))
    if mode not in SUPPORTED_MODES:
        mode = "sim"

    default_pose = _default_position(context)
    position = _normalize_pose(state.get("position"), default_pose)
    target = _normalize_pose(state.get("target"), position)
    position_validation = validate_position(context, position)
    target_validation = validate_target(context, target["x"], target["y"], target["z"])

    legacy_sim_state = (
        mode == "sim"
        and "limits_verified" not in state
        and "motor_direction_ok" not in state
    )
    calibration_defaults = _calibration_defaults(context, mode, position_validation["lengths"], legacy_sim_state)

    raw_homed = calibration_defaults["homed"] if legacy_sim_state else (state.get("homed") if isinstance(state.get("homed"), dict) else calibration_defaults["homed"])
    homed = _ordered_bool_map(raw_homed, context.cable_names)
    raw_motor_direction_ok = calibration_defaults["motor_direction_ok"] if legacy_sim_state else (state.get("motor_direction_ok") if isinstance(state.get("motor_direction_ok"), dict) else calibration_defaults["motor_direction_ok"])
    motor_direction_ok = _ordered_bool_map(raw_motor_direction_ok, context.cable_names)
    limits_verified = bool(calibration_defaults["limits_verified"] if legacy_sim_state else state.get("limits_verified", calibration_defaults["limits_verified"]))

    step_state = state.get("steps") if isinstance(state.get("steps"), dict) else {}
    spool_state = state.get("spools") if isinstance(state.get("spools"), dict) else {}
    path_state = state.get("path") if isinstance(state.get("path"), dict) else {}
    lengths = _normalize_lengths(state.get("lengths"), position_validation["lengths"], context.cable_names)
    target_lengths = _normalize_lengths(state.get("target_lengths"), target_validation["lengths"], context.cable_names)

    raw_zero_lengths = calibration_defaults["zero_lengths_m"] if legacy_sim_state else (state.get("zero_lengths_m") if isinstance(state.get("zero_lengths_m"), dict) else calibration_defaults["zero_lengths_m"])
    zero_lengths_m = _ordered_float_map(raw_zero_lengths, context.cable_names, calibration_defaults["zero_lengths_m"])
    raw_line_offsets = calibration_defaults["line_offsets_steps"] if legacy_sim_state else (state.get("line_offsets_steps") if isinstance(state.get("line_offsets_steps"), dict) else calibration_defaults["line_offsets_steps"])
    line_offsets_steps = _ordered_int_map(raw_line_offsets, context.cable_names, calibration_defaults["line_offsets_steps"])

    faults = [fault for fault in state.get("faults", []) if fault != "invalid_geometry"]
    if not geometry["valid"]:
        faults.append("invalid_geometry")

    controller_ready = bool(state.get("controller_ready", mode == "sim")) and bool(geometry["valid"])
    calibration_valid = _calibration_valid(homed, motor_direction_ok, limits_verified)

    warnings = [warning for warning in state.get("warnings", []) if warning not in DERIVED_WARNING_KEYS]
    warnings.extend(_calibration_warnings(homed, motor_direction_ok, limits_verified))
    if not position_validation["valid"]:
        warnings.append("workspace_invalid")
    if not target_validation["valid"]:
        warnings.append("target_invalid")
    if not controller_ready:
        warnings.append("controller_not_ready")

    return {
        "mode": mode,
        "status": "estopped" if state.get("estop") else str(state.get("status", "idle")),
        "estop": bool(state.get("estop", False)),
        "armed": bool(state.get("armed", True)),
        "controller_ready": controller_ready,
        "controller_detail": state.get("controller_detail"),
        "geometry_valid": bool(geometry["valid"]),
        "workspace_valid": bool(position_validation["valid"]),
        "calibration_valid": calibration_valid,
        "faults": faults,
        "warnings": warnings,
        "last_error": state.get("last_error"),
        "homed": homed,
        "limits_verified": limits_verified,
        "motor_direction_ok": motor_direction_ok,
        "zero_lengths_m": zero_lengths_m,
        "line_offsets_steps": line_offsets_steps,
        "controller_trace": list(state.get("controller_trace", []))[-50:],
        "position": position,
        "target": target,
        "speed": float(state.get("speed", 0.4)),
        "anchors": {name: list(coords) for name, coords in context.anchors.items()},
        "bounds": {axis: list(axis_range) for axis, axis_range in context.bounds.items()},
        "lengths": lengths,
        "target_lengths": target_lengths,
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
