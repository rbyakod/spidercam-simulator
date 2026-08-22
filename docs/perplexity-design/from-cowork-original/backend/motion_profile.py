from __future__ import annotations
from math import sqrt, ceil

def trapezoid_profile(total_steps, v_start, v_max, accel_steps_s2):
    total_steps = abs(int(total_steps))
    if total_steps == 0:
        return []
    v_start = max(1, int(v_start))
    v_max = max(v_start, int(v_max))
    a = max(1, int(accel_steps_s2))
    accel_dist = max(0, int((v_max*v_max - v_start*v_start) / (2*a)))
    decel_dist = accel_dist
    if accel_dist + decel_dist > total_steps:
        accel_dist = total_steps // 2
        decel_dist = total_steps - accel_dist
        v_peak = int(sqrt(max(v_start*v_start + 2*a*accel_dist, 1)))
    else:
        v_peak = v_max
    cruise_dist = total_steps - accel_dist - decel_dist
    segments = []

    def chunk_steps(dist, start_v, sign):
        out = []
        consumed = 0
        while consumed < dist:
            v = int(sqrt(max(start_v*start_v + 2*a*consumed, 1)))
            v = min(v, v_peak)
            n = min(ceil(v / 25), dist - consumed)
            out.append((v, n, sign))
            consumed += n
        return out

    segments.extend(chunk_steps(accel_dist, v_start, +1))
    if cruise_dist > 0:
        segments.append((v_peak, cruise_dist, 0))
    decel_consumed = 0
    while decel_consumed < decel_dist:
        remaining = decel_dist - decel_consumed
        v = int(sqrt(max(v_start*v_start + 2*a*remaining, 1)))
        v = min(max(v, v_start), v_peak)
        n = min(ceil(v / 25), remaining)
        segments.append((v, n, -1))
        decel_consumed += n
    return segments

def dda_sync_plan(step_targets: dict[str, int], v_start: int, v_max: int, accel_steps_s2: int):
    abs_steps = {k: abs(v) for k, v in step_targets.items()}
    master = max(abs_steps.values()) if abs_steps else 0
    if master == 0:
        return []
    ramp = trapezoid_profile(master, v_start, v_max, accel_steps_s2)
    acc = {k: 0 for k in step_targets}
    signed = {k: (1 if step_targets[k] >= 0 else -1) for k in step_targets}
    out = []
    for freq, master_steps, phase in ramp:
        pulses = []
        for _ in range(master_steps):
            mask = {}
            for k in step_targets:
                acc[k] += abs_steps[k]
                do_step = 0
                if acc[k] >= master:
                    acc[k] -= master
                    do_step = signed[k]
                mask[k] = do_step
            pulses.append(mask)
        out.append({"freq_hz": freq, "steps": master_steps, "phase": phase, "pulses": pulses})
    return out
