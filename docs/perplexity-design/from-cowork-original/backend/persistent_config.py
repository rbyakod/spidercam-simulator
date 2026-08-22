from __future__ import annotations
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, List, Optional
from pathlib import Path
import yaml, tempfile, os

CONFIG_PATH = Path("data/spiderpi.yaml")
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

class MotorPinConfig(BaseModel):
    step: int
    dir: int
    en: Optional[int] = None
    invert_dir: bool = False

class MotorTuning(BaseModel):
    rated_current_a: float = 1.7
    holding_torque_nm: float = 0.42
    drv8825_vref: float = 0.75
    microsteps: int = 16
    start_freq_hz: int = 250
    max_freq_hz: int = 2200
    accel_steps_s2: int = 7000

class FrameConfig(BaseModel):
    anchors: Dict[str, List[float]] = Field(default_factory=lambda: {
        "A": [0.0, 0.0, 1.5], "B": [2.0, 0.0, 1.5],
        "C": [2.0, 2.0, 1.5], "D": [0.0, 2.0, 1.5],
    })
    bounds: Dict[str, List[float]] = Field(default_factory=lambda: {
        "x": [0.2, 1.8], "y": [0.2, 1.8], "z": [0.3, 1.3],
    })
    spool_radius_m: float = 0.011
    motor_steps_per_rev: int = 200

class RigConfig(BaseModel):
    carriage_mass_kg: float = 0.40
    payload_mass_kg: float = 0.08
    gravity: float = 9.81
    cable_drag_coeff: float = 0.08
    max_speed_mps: float = 0.7
    max_accel_mps2: float = 0.9

class CalibrationState(BaseModel):
    homed: Dict[str, bool] = Field(default_factory=lambda: {"A":False,"B":False,"C":False,"D":False})
    zero_lengths_m: Dict[str, float] = Field(default_factory=lambda: {"A":0.0,"B":0.0,"C":0.0,"D":0.0})
    line_offsets_steps: Dict[str, int] = Field(default_factory=lambda: {"A":0,"B":0,"C":0,"D":0})
    measured_spool_radius_m: Optional[float] = None
    motor_direction_ok: Dict[str, bool] = Field(default_factory=lambda: {"A":False,"B":False,"C":False,"D":False})
    limits_verified: bool = False
    notes: List[str] = Field(default_factory=list)

class SystemConfig(BaseModel):
    frame: FrameConfig = Field(default_factory=FrameConfig)
    rig: RigConfig = Field(default_factory=RigConfig)
    motors: MotorTuning = Field(default_factory=MotorTuning)
    gpio_map: Dict[str, MotorPinConfig] = Field(default_factory=lambda: {
        "A": MotorPinConfig(step=12, dir=5, en=6),
        "B": MotorPinConfig(step=13, dir=16, en=6),
        "C": MotorPinConfig(step=19, dir=20, en=6),
        "D": MotorPinConfig(step=26, dir=21, en=6),
    })
    limit_switches: Dict[str, int] = Field(default_factory=lambda: {
        "A": 17, "B": 27, "C": 22, "D": 23,
    })
    calibration: CalibrationState = Field(default_factory=CalibrationState)

DEFAULT_CONFIG = SystemConfig()

def load_config() -> SystemConfig:
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    raw = yaml.safe_load(CONFIG_PATH.read_text()) or {}
    try:
        return SystemConfig.model_validate(raw)
    except ValidationError:
        CONFIG_PATH.with_suffix(".invalid.yaml").write_text(CONFIG_PATH.read_text())
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(cfg: SystemConfig):
    payload = yaml.safe_dump(cfg.model_dump(mode="python"), sort_keys=False)
    with tempfile.NamedTemporaryFile("w", delete=False,
                                     dir=str(CONFIG_PATH.parent), suffix=".tmp") as tf:
        tf.write(payload)
        tmp = tf.name
    os.replace(tmp, CONFIG_PATH)

def update_config(mutator):
    cfg = load_config()
    mutator(cfg)
    save_config(cfg)
    return cfg
