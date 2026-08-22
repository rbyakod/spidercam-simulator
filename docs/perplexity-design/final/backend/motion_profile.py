from __future__ import annotations
from dataclasses import dataclass, field
import yaml, pathlib
from config import settings

@dataclass
class MotionProfile:
    name: str
    max_speed: float = 0.3
    max_accel: float = 0.6
    jerk_limit: float = None
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "max_speed": self.max_speed,
            "max_accel": self.max_accel,
            "jerk_limit": self.jerk_limit,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d: dict):
        fields = {"name", "max_speed", "max_accel", "jerk_limit", "description"}
        return cls(**{k: v for k, v in d.items() if k in fields})

DEFAULT_PROFILES = [
    MotionProfile("slow",      max_speed=0.1, max_accel=0.2, description="Safe slow mode"),
    MotionProfile("normal",    max_speed=0.3, max_accel=0.6, description="Default operation"),
    MotionProfile("fast",      max_speed=0.5, max_accel=1.0, description="High-speed mode"),
    MotionProfile("precision", max_speed=0.05, max_accel=0.1, jerk_limit=0.5, description="Ultra-slow"),
]

class ProfileStore:
    def __init__(self) -> None:
        self._path = pathlib.Path(settings.profile_path) / "machine_profiles.yaml"
        self._profiles = {p.name: p for p in DEFAULT_PROFILES}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            data = yaml.safe_load(self._path.read_text()) or []
            for d in data:
                p = MotionProfile.from_dict(d)
                self._profiles[p.name] = p

    def list(self) -> list:
        return [p.to_dict() for p in self._profiles.values()]

    def get(self, name: str):
        return self._profiles.get(name)

    def save(self, profile) -> None:
        self._profiles[profile.name] = profile
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(yaml.dump([p.to_dict() for p in self._profiles.values()]))

    def delete(self, name: str) -> bool:
        if name in self._profiles:
            del self._profiles[name]
            self._path.write_text(yaml.dump([p.to_dict() for p in self._profiles.values()]))
            return True
        return False

profile_store = ProfileStore()
