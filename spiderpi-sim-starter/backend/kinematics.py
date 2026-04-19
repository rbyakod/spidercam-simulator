from __future__ import annotations

from math import pi, sqrt
from typing import Dict, Mapping, Sequence

from models import RuntimeContext


def lengths_from_xyz(
    anchors: Mapping[str, Sequence[float]],
    x: float,
    y: float,
    z: float,
) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for name, (ax, ay, az) in anchors.items():
        out[name] = sqrt((x - ax) ** 2 + (y - ay) ** 2 + (z - az) ** 2)
    return out


def lengths_from_position(context: RuntimeContext, position: Mapping[str, float]) -> Dict[str, float]:
    return lengths_from_xyz(
        context.anchors,
        float(position["x"]),
        float(position["y"]),
        float(position["z"]),
    )


def steps_from_delta_length(delta_len: float, context: RuntimeContext) -> int:
    if context.spool_radius_m <= 0:
        return 0
    revs = delta_len / (2 * pi * context.spool_radius_m)
    return int(revs * context.motor_steps_per_rev * context.microsteps)


def _solve_linear_3x3(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> list[float] | None:
    rows = [list(row) + [float(value)] for row, value in zip(matrix, vector)]

    for pivot_index in range(3):
        pivot_row = max(range(pivot_index, 3), key=lambda idx: abs(rows[idx][pivot_index]))
        if abs(rows[pivot_row][pivot_index]) < 1e-9:
            return None
        if pivot_row != pivot_index:
            rows[pivot_index], rows[pivot_row] = rows[pivot_row], rows[pivot_index]

        divisor = rows[pivot_index][pivot_index]
        for column in range(pivot_index, 4):
            rows[pivot_index][column] /= divisor

        for row_index in range(3):
            if row_index == pivot_index:
                continue
            factor = rows[row_index][pivot_index]
            for column in range(pivot_index, 4):
                rows[row_index][column] -= factor * rows[pivot_index][column]

    return [rows[index][3] for index in range(3)]


def solve_position_from_lengths(
    context: RuntimeContext,
    lengths: Mapping[str, float],
    initial_guess: Mapping[str, float] | None = None,
    max_iterations: int = 24,
) -> Dict[str, object]:
    if initial_guess is None:
        x = (context.bounds["x"][0] + context.bounds["x"][1]) / 2
        y = (context.bounds["y"][0] + context.bounds["y"][1]) / 2
        z = (context.bounds["z"][0] + context.bounds["z"][1]) / 2
    else:
        x = float(initial_guess["x"])
        y = float(initial_guess["y"])
        z = float(initial_guess["z"])

    last_residual = float("inf")
    for _ in range(max_iterations):
        jt_j = [
            [1e-6, 0.0, 0.0],
            [0.0, 1e-6, 0.0],
            [0.0, 0.0, 1e-6],
        ]
        jt_r = [0.0, 0.0, 0.0]
        residual_norm_sq = 0.0

        for name, (ax, ay, az) in context.anchors.items():
            dx = x - ax
            dy = y - ay
            dz = z - az
            distance = sqrt(dx * dx + dy * dy + dz * dz)
            if distance < 1e-9:
                distance = 1e-9
            residual = distance - float(lengths[name])
            jacobian = [dx / distance, dy / distance, dz / distance]
            residual_norm_sq += residual * residual

            for row in range(3):
                jt_r[row] += jacobian[row] * residual
                for column in range(3):
                    jt_j[row][column] += jacobian[row] * jacobian[column]

        delta = _solve_linear_3x3(jt_j, [-value for value in jt_r])
        if delta is None:
            break

        x += delta[0]
        y += delta[1]
        z += delta[2]

        step_norm = sqrt(delta[0] * delta[0] + delta[1] * delta[1] + delta[2] * delta[2])
        last_residual = sqrt(residual_norm_sq)
        if step_norm < 1e-7 or last_residual < 1e-7:
            return {
                "success": True,
                "position": {"x": x, "y": y, "z": z},
                "residual": last_residual,
            }

    return {
        "success": last_residual < 1e-4,
        "position": {"x": x, "y": y, "z": z},
        "residual": last_residual,
    }
