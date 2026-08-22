from __future__ import annotations
from config import settings

def create_executor():
    if settings.sim_mode:
        from sim_backend import sim_executor
        return sim_executor
    else:
        from gpio_backend import load_gpio_map
        from gpio_runtime import GPIORuntime
        gpio_map = load_gpio_map()
        rt = GPIORuntime(gpio_map)
        rt._setup()
        rt._enable(True)
        return rt
