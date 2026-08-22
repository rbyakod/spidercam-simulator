from __future__ import annotations
import yaml, pathlib

GPIO_MAP = {
    "axes": [
        {"name": "FL", "step_pin": 17, "dir_pin": 18, "enable_pin": 27},
        {"name": "FR", "step_pin": 22, "dir_pin": 23, "enable_pin": 24},
        {"name": "RL", "step_pin":  5, "dir_pin":  6, "enable_pin": 13},
        {"name": "RR", "step_pin": 19, "dir_pin": 26, "enable_pin": 21},
    ],
    "limit_pins": [4, 25, 12, 16],
    "microstep_pins": {"M0": 8, "M1": 7, "M2": 1},
}

out = pathlib.Path("data/spiderpi.yaml")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(yaml.dump(GPIO_MAP, default_flow_style=False))
print(f"Written GPIO map to {out}")
