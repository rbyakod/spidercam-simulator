from __future__ import annotations
import yaml, pathlib
from config import settings

_cfg_path = pathlib.Path(settings.gpio_config_path)

def load() -> dict:
    if _cfg_path.exists():
        return yaml.safe_load(_cfg_path.read_text()) or {}
    return {}

def save(data: dict) -> None:
    _cfg_path.parent.mkdir(parents=True, exist_ok=True)
    _cfg_path.write_text(yaml.dump(data, default_flow_style=False))
