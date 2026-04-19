from __future__ import annotations

import time
from typing import Dict

from kinematics import lengths_from_position, steps_from_delta_length
from models import RuntimeContext


class SimController:
    def __init__(self, context: RuntimeContext):
        self.context = context

    def is_ready(self) -> bool:
        return True

    def apply_pose(self, state: Dict[str, object], next_position: Dict[str, float]) -> None:
        previous_lengths = state.get("lengths") or lengths_from_position(self.context, state["position"])
        next_lengths = lengths_from_position(self.context, next_position)

        for name in self.context.cable_names:
            delta_length = next_lengths[name] - previous_lengths[name]
            state["steps"][name] += steps_from_delta_length(delta_length, self.context)
            if self.context.spool_radius_m > 0:
                state["spools"][name] += delta_length / self.context.spool_radius_m

        state["position"] = dict(next_position)
        state["lengths"] = next_lengths
        state["updated_at"] = time.time()
        trail = list(state.get("trail", []))
        trail.append(dict(next_position))
        state["trail"] = trail[-250:]
