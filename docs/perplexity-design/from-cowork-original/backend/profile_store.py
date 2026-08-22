from __future__ import annotations
from pathlib import Path
import yaml, tempfile, os

PROFILES_FILE = Path("profiles/machine_profiles.yaml")
PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)

def _atomic_write(path: Path, text: str):
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), suffix=".tmp") as tf:
        tf.write(text)
        tmp = tf.name
    os.replace(tmp, path)

def load_profiles() -> dict:
    if not PROFILES_FILE.exists():
        return {}
    return yaml.safe_load(PROFILES_FILE.read_text()) or {}

def list_profiles() -> list[str]:
    return list(load_profiles().keys())

def get_profile(name: str) -> dict | None:
    return load_profiles().get(name)

def save_profile(name: str, profile: dict):
    all_profiles = load_profiles()
    all_profiles[name] = profile
    _atomic_write(PROFILES_FILE, yaml.safe_dump(all_profiles, sort_keys=False))

def delete_profile(name: str):
    all_profiles = load_profiles()
    all_profiles.pop(name, None)
    _atomic_write(PROFILES_FILE, yaml.safe_dump(all_profiles, sort_keys=False))

def export_as_yaml(name: str, profile: dict) -> str:
    return yaml.safe_dump({name: profile}, sort_keys=False)
