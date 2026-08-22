from __future__ import annotations
import numpy as np
from config import settings

def _trapezoidal_profile(d: float, v_max: float, a_max: float, dt: float):
    t_acc = v_max / a_max
    d_acc = 0.5 * a_max * t_acc ** 2
    if 2 * d_acc >= d:
        t_acc = np.sqrt(d / a_max)
        t_total = 2 * t_acc
        v_peak = a_max * t_acc
    else:
        d_flat = d - 2 * d_acc
        t_flat = d_flat / v_max
        t_total = 2 * t_acc + t_flat
        v_peak = v_max
    ts = np.arange(0, t_total, dt)
    pos = np.zeros_like(ts)
    for i, t in enumerate(ts):
        if t <= t_acc:
            pos[i] = 0.5 * a_max * t ** 2
        elif t <= t_total - t_acc:
            pos[i] = 0.5 * a_max * t_acc ** 2 + v_peak * (t - t_acc)
        else:
            tr = t_total - t
            pos[i] = d - 0.5 * a_max * tr ** 2
    return ts, pos

def interpolate_path(waypoints: list, dt: float = 0.02) -> list:
    trajectory = []
    for i in range(len(waypoints) - 1):
        p0 = np.array(waypoints[i], dtype=float)
        p1 = np.array(waypoints[i + 1], dtype=float)
        seg = p1 - p0
        d = float(np.linalg.norm(seg))
        if d < 1e-6:
            continue
        direction = seg / d
        _, s = _trapezoidal_profile(d, settings.max_speed, settings.max_accel, dt)
        for si in s:
            trajectory.append(p0 + direction * si)
    return trajectory
