from __future__ import annotations
import yaml, pathlib
from config import settings

def load_gpio_map() -> dict:
    path = pathlib.Path(settings.gpio_config_path)
    if path.exists():
        return yaml.safe_load(path.read_text()) or {}
    return {}

def save_gpio_map(gpio_map: dict) -> None:
    path = pathlib.Path(settings.gpio_config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(gpio_map, default_flow_style=False))
