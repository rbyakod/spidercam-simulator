from __future__ import annotations
import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    frame_width: float = Field(1.0, env="FRAME_WIDTH")
    frame_height: float = Field(1.0, env="FRAME_HEIGHT")
    frame_depth: float = Field(1.0, env="FRAME_DEPTH")
    max_speed: float = Field(0.5, env="MAX_SPEED")
    max_accel: float = Field(1.0, env="MAX_ACCEL")
    max_cable_tension: float = Field(50.0, env="MAX_CABLE_TENSION")
    min_cable_tension: float = Field(2.0, env="MIN_CABLE_TENSION")
    steps_per_rev: int = Field(200, env="STEPS_PER_REV")
    microsteps: int = Field(16, env="MICROSTEPS")
    spool_diameter_mm: float = Field(40.0, env="SPOOL_DIAMETER_MM")
    gpio_config_path: str = Field("data/spiderpi.yaml", env="GPIO_CONFIG_PATH")
    sim_mode: bool = Field(True, env="SPIDERPI_SIM_GPIO")
    ws_tick_hz: float = Field(50.0, env="WS_TICK_HZ")
    profile_path: str = Field("data/profiles", env="PROFILE_PATH")
    path_store_path: str = Field("data/path_presets.yaml", env="PATH_STORE_PATH")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

def steps_per_metre() -> float:
    circ = settings.spool_diameter_mm * 3.14159265 / 1000.0
    return settings.steps_per_rev * settings.microsteps / circ
