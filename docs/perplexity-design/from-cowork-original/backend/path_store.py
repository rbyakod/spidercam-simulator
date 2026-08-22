from __future__ import annotations
from pathlib import Path
import yaml, tempfile, os

PATHS_FILE = Path("data/path_presets.yaml")
PATHS_FILE.parent.mkdir(parents=True, exist_ok=True)

DEFAULT = {
    "paths": {
        "square_demo": {
            "type": "waypoints",
            "speed": 0.25,
            "points": [
                {"x": 0.6, "y": 0.6, "z": 0.9, "speed": 0.25},
                {"x": 1.4, "y": 0.6, "z": 0.9, "speed": 0.25},
                {"x": 1.4, "y": 1.4, "z": 0.9, "speed": 0.25},
                {"x": 0.6, "y": 1.4, "z": 0.9, "speed": 0.25},
                {"x": 0.6, "y": 0.6, "z": 0.9, "speed": 0.25},
            ]
        }
    },
    "poses": {
        "center": {"x": 1.0, "y": 1.0, "z": 0.9}
    }
}

def _atomic_write(path: Path, text: str):
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), suffix=".tmp") as tf:
        tf.write(text)
        tmp = tf.name
    os.replace(tmp, path)

def load_paths():
    if not PATHS_FILE.exists():
        save_paths(DEFAULT)
        return DEFAULT
    return yaml.safe_load(PATHS_FILE.read_text()) or DEFAULT

def save_paths(data: dict):
    _atomic_write(PATHS_FILE, yaml.safe_dump(data, sort_keys=False))

def list_paths():
    data = load_paths()
    return data.get("paths", {}), data.get("poses", {})

def upsert_path(name: str, payload: dict):
    data = load_paths()
    data.setdefault("paths", {})[name] = payload
    save_paths(data)
    return data["paths"][name]

def delete_path(name: str):
    data = load_paths()
    data.setdefault("paths", {}).pop(name, None)
    save_paths(data)

def upsert_pose(name: str, pose: dict):
    data = load_paths()
    data.setdefault("poses", {})[name] = pose
    save_paths(data)
    return data["poses"][name]
