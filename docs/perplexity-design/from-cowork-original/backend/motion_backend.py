from __future__ import annotations
from abc import ABC, abstractmethod

class MotionBackend(ABC):
    @abstractmethod
    def mode(self) -> str: ...

    @abstractmethod
    def move_step_deltas(self, deltas: dict[str, int]) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def read_switches(self) -> dict[str, bool]: ...

    @abstractmethod
    def close(self) -> None: ...
