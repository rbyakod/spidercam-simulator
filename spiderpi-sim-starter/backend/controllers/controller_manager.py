from __future__ import annotations

from typing import Dict

from controllers.base_controller import BaseController


class ControllerManager:
    def __init__(self, controllers: Dict[str, BaseController]):
        self.controllers = controllers

    def get(self, mode: str) -> BaseController:
        return self.controllers.get(mode, self.controllers["sim"])

    def supported_modes(self) -> tuple[str, ...]:
        return tuple(self.controllers.keys())
