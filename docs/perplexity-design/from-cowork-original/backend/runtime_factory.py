from __future__ import annotations
from persistent_config import load_config
from sim_backend import SimMotionBackend
from gpio_backend import GPIOMotionBackend

def build_backend(on_limit):
    cfg = load_config()
    try:
        backend = GPIOMotionBackend(cfg, on_limit=on_limit)
        return backend
    except Exception:
        return SimMotionBackend()
