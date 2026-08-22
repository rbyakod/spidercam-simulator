from __future__ import annotations
from pathlib import Path
import yaml, tempfile, os

WIZARD_FILE = Path("data/calibration_wizard.yaml")
WIZARD_FILE.parent.mkdir(parents=True, exist_ok=True)

CHECKLIST_STEPS = [
    {"id": "frame_sizing", "title": "Frame Sizing & Profile", "tasks": [
        "Apply a machine profile (desktop_1m, room_1p5m, or room_2m)",
        "Verify anchor coordinates match physical frame",
        "Confirm spool radius setting matches measured value",
    ]},
    {"id": "visual_geometry", "title": "Visual Geometry Check", "tasks": [
        "View 3D scene — cables should point to correct corners",
        "Move to center position in sim and confirm visually",
        "Check bounds are within physical frame dimensions",
    ]},
    {"id": "io_check", "title": "Wiring and I/O Check", "tasks": [
        "Verify all limit switches read idle (not triggered) at rest",
        "Verify E-stop button reads correct idle state",
        "Check motor enable signals activate correctly",
    ]},
    {"id": "motor_direction", "title": "Motor Direction Verification", "tasks": [
        "Jog motor A forward (+) — spool should wind cable in",
        "Jog motor B forward (+) — spool should wind cable in",
        "Jog motor C forward (+) — spool should wind cable in",
        "Jog motor D forward (+) — spool should wind cable in",
        "Mark each axis as direction-verified in dashboard",
    ]},
    {"id": "homing", "title": "Homing All Axes", "tasks": [
        "Home axis A — confirm switch triggers and position resets",
        "Home axis B — confirm switch triggers and position resets",
        "Home axis C — confirm switch triggers and position resets",
        "Home axis D — confirm switch triggers and position resets",
    ]},
    {"id": "spool_radius", "title": "Spool Radius Calibration", "tasks": [
        "Mark spool with tape or pen",
        "Command exactly 20 full revolutions",
        "Measure actual cable travel distance",
        "Calculate: radius = travel / (20 * 2 * pi)",
        "Enter measured radius in dashboard and save",
    ]},
    {"id": "center_zero", "title": "Center and Zero Calibration", "tasks": [
        "Command carriage to logical center (1.0, 1.0, 0.9)",
        "Physically confirm carriage is centered",
        "Record zero cable lengths at this position",
        "Save zero offsets to config",
    ]},
    {"id": "bounds_verify", "title": "Bounds Verification", "tasks": [
        "Move to each corner at low speed",
        "Verify no mechanical interference at extremes",
        "Confirm E-stop works during motion",
        "Save verified bounds to config",
    ]},
    {"id": "path_test", "title": "Path Validation", "tasks": [
        "Run square path at 0.15 m/s — confirm shape",
        "Run circle path at 0.15 m/s — confirm shape",
        "Mark both paths as passed in dashboard",
    ]},
]

def _atomic_write(path: Path, text: str):
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), suffix=".tmp") as tf:
        tf.write(text)
        tmp = tf.name
    os.replace(tmp, path)

def load_wizard():
    if not WIZARD_FILE.exists():
        return _default_wizard()
    return yaml.safe_load(WIZARD_FILE.read_text()) or _default_wizard()

def _default_wizard():
    return {
        "steps": {s["id"]: {"done": False, "notes": ""} for s in CHECKLIST_STEPS},
        "version": 1,
    }

def save_wizard(data: dict):
    _atomic_write(WIZARD_FILE, yaml.safe_dump(data, sort_keys=False))

def get_wizard_with_checklist():
    state = load_wizard()
    result = []
    for step in CHECKLIST_STEPS:
        sid = step["id"]
        s = state["steps"].get(sid, {"done": False, "notes": ""})
        result.append({
            "id": sid,
            "title": step["title"],
            "tasks": step["tasks"],
            "done": s.get("done", False),
            "notes": s.get("notes", ""),
        })
    return result

def mark_step(step_id: str, done: bool, notes: str = ""):
    state = load_wizard()
    state["steps"].setdefault(step_id, {})["done"] = done
    state["steps"][step_id]["notes"] = notes
    save_wizard(state)

def reset_wizard():
    save_wizard(_default_wizard())
