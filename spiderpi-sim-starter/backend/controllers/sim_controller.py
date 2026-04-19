from __future__ import annotations

import time
from typing import Dict

from kinematics import solve_position_from_lengths, steps_from_delta_length
from models import RuntimeContext


class SimController:
    def __init__(self, context: RuntimeContext):
        self.context = context

    def is_ready(self) -> bool:
        return True

    def apply_lengths(self, state: Dict[str, object], next_lengths: Dict[str, float]) -> None:
        previous_lengths = state["lengths"]
        for name in self.context.cable_names:
            delta_length = next_lengths[name] - previous_lengths[name]
            state["steps"][name] += steps_from_delta_length(delta_length, self.context)
            if self.context.spool_radius_m > 0:
                state["spools"][name] += delta_length / self.context.spool_radius_m

        solved_pose = solve_position_from_lengths(
            self.context,
            next_lengths,
            initial_guess=state["position"],
        )
        state["position"] = dict(solved_pose["position"])
        state["lengths"] = dict(next_lengths)
        state["updated_at"] = time.time()
        trail = list(state.get("trail", []))
        trail.append(dict(state["position"]))
        state["trail"] = trail[-250:]
