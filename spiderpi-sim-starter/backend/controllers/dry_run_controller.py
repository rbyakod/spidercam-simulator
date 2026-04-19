from __future__ import annotations

from typing import Dict

from controllers.sim_controller import SimController


class DryRunController(SimController):
    mode = "dry_run"

    def apply_lengths(self, state: Dict[str, object], next_lengths: Dict[str, float]) -> None:
        previous_lengths = state["lengths"]
        delta_summary = ", ".join(
            f"{name}:{next_lengths[name] - previous_lengths[name]:+.4f}m"
            for name in self.context.cable_names
        )
        self.append_trace(state, f"dry_run: apply_lengths {delta_summary}")
        super().apply_lengths(state, next_lengths)
