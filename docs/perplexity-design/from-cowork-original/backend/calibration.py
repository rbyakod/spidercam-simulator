from __future__ import annotations
from pydantic import BaseModel
from typing import Dict, Optional
from persistent_config import load_config, save_config

WIZARD_ORDER = [
    "safety_check", "motor_direction", "home_switch_test",
    "spool_radius_measure", "line_zero", "center_position",
    "bounds_verify", "finalize"
]

def get_wizard_state():
    cfg = load_config()
    cal = cfg.calibration
    return {
        "current": current_step(cfg),
        "steps": [
            {"step": "safety_check", "done": False,
             "instructions": "Verify frame is rigid, carriage is unloaded/light, E-stop is wired."},
            {"step": "motor_direction", "done": all(cal.motor_direction_ok.values()),
             "instructions": "Jog each motor +100 steps and confirm intended spool direction."},
            {"step": "home_switch_test", "done": all(cal.homed.values()),
             "instructions": "Run each winch toward its homing switch and confirm trigger."},
            {"step": "spool_radius_measure", "done": cal.measured_spool_radius_m is not None,
             "instructions": "Mark spool, rotate exactly 20 turns, measure line travel, divide by 20*2*pi."},
            {"step": "line_zero", "done": any(v != 0 for v in cal.zero_lengths_m.values()),
             "instructions": "Move carriage to center reference position and record cable lengths."},
            {"step": "center_position", "done": False,
             "instructions": "Command move to logical center and fine-adjust until visually centered."},
            {"step": "bounds_verify", "done": cal.limits_verified,
             "instructions": "Check safe XY and Z limits at very low speed and record them."},
            {"step": "finalize",
             "done": cal.limits_verified and all(cal.motor_direction_ok.values()),
             "instructions": "Save configuration and export a calibration report."},
        ]
    }

def current_step(cfg):
    cal = cfg.calibration
    if not all(cal.motor_direction_ok.values()): return "motor_direction"
    if not all(cal.homed.values()): return "home_switch_test"
    if cal.measured_spool_radius_m is None: return "spool_radius_measure"
    if not any(v != 0 for v in cal.zero_lengths_m.values()): return "line_zero"
    if not cal.limits_verified: return "bounds_verify"
    return "finalize"

def set_motor_direction(axis: str, invert_dir: bool, ok: bool):
    cfg = load_config()
    cfg.gpio_map[axis].invert_dir = invert_dir
    cfg.calibration.motor_direction_ok[axis] = ok
    save_config(cfg)
    return cfg

def set_homed(axis: str, homed: bool):
    cfg = load_config()
    cfg.calibration.homed[axis] = homed
    save_config(cfg)
    return cfg

def set_spool_radius(radius_m: float):
    cfg = load_config()
    cfg.frame.spool_radius_m = radius_m
    cfg.calibration.measured_spool_radius_m = radius_m
    save_config(cfg)
    return cfg

def set_zero_lengths(lengths: Dict[str, float]):
    cfg = load_config()
    cfg.calibration.zero_lengths_m.update(lengths)
    save_config(cfg)
    return cfg

def set_line_offsets(offsets: Dict[str, int]):
    cfg = load_config()
    cfg.calibration.line_offsets_steps.update(offsets)
    save_config(cfg)
    return cfg

def set_bounds(xmin, xmax, ymin, ymax, zmin, zmax):
    cfg = load_config()
    cfg.frame.bounds = {"x": [xmin, xmax], "y": [ymin, ymax], "z": [zmin, zmax]}
    cfg.calibration.limits_verified = True
    save_config(cfg)
    return cfg
