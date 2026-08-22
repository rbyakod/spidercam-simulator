from __future__ import annotations

GATE_REQUIREMENTS = {
    "safety_check": ["profile_loaded"],
    "motor_direction": ["profile_loaded"],
    "home_switch_test": ["all_directions_ok"],
    "spool_radius_measure": ["all_homed"],
    "line_zero": ["spool_radius_measured"],
    "center_position": ["spool_radius_measured"],
    "bounds_verify": ["center_calibrated"],
    "finalize": ["bounds_verified", "path_square_ok", "path_circle_ok"],
}

def compute_gates(hardware_state: dict, homing_state: dict, cfg) -> dict:
    gates = {}
    profile_loaded = cfg is not None
    all_dir_ok = all(homing_state.get("axis_direction_ok", {}).values())
    all_homed = all(homing_state.get("axis_homed", {}).values())
    sw = hardware_state.get("switches", {})
    switches_idle = all(not v for v in sw.values())
    estop_ok = not hardware_state.get("estop_input", False)
    gates["profile_loaded"] = profile_loaded
    gates["all_directions_ok"] = all_dir_ok
    gates["all_homed"] = all_homed
    gates["switches_idle"] = switches_idle
    gates["estop_ok"] = estop_ok
    gates["spool_radius_measured"] = homing_state.get("spool_radius_measured", False)
    gates["center_calibrated"] = homing_state.get("center_calibrated", False)
    gates["preload_ok"] = homing_state.get("preload_ok", False)
    gates["bounds_verified"] = homing_state.get("bounds_verified", False)
    gates["path_square_ok"] = homing_state.get("path_square_ok", False)
    gates["path_circle_ok"] = homing_state.get("path_circle_ok", False)
    return gates

def step_gate_status(step_name: str, gates: dict) -> dict:
    reqs = GATE_REQUIREMENTS.get(step_name, [])
    satisfied = {r: gates.get(r, False) for r in reqs}
    all_ok = all(satisfied.values())
    return {"satisfied": all_ok, "requirements": satisfied}
