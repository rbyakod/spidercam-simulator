from __future__ import annotations
import yaml, pathlib
from config import settings

class PathStore:
    def __init__(self) -> None:
        self._path = pathlib.Path(settings.path_store_path)
        self._presets = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            data = yaml.safe_load(self._path.read_text()) or {}
            self._presets = data.get("presets", {})

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(yaml.dump({"presets": self._presets}))

    def list(self) -> list:
        return list(self._presets.keys())

    def get(self, name: str):
        return self._presets.get(name)

    def save(self, name: str, waypoints: list) -> None:
        self._presets[name] = waypoints
        self._save()

    def delete(self, name: str) -> bool:
        if name in self._presets:
            del self._presets[name]
            self._save()
            return True
        return False

path_store = PathStore()
