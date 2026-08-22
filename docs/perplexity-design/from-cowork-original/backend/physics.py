from math import sqrt
from config import FRAME, MOTORS, RIG

anchors = FRAME["anchors"]
spool_radius = FRAME["spool_radius_m"]

def vec_len(x, y, z):
    return sqrt(x*x + y*y + z*z)

def unit_vec(ax, ay, az, px, py, pz):
    dx, dy, dz = ax-px, ay-py, az-pz
    L = vec_len(dx, dy, dz)
    if L == 0:
        return (0.0, 0.0, 0.0), 0.0
    return (dx/L, dy/L, dz/L), L

def drv8825_current_limit(vref=0.75, rsense=0.1):
    return 2.0 * vref

def available_torque_nm(speed_mps: float):
    base = MOTORS["holding_torque_nm"]
    s = max(0.0, min(speed_mps / max(RIG["max_speed_mps"], 1e-6), 1.5))
    drop = 1.0 - 0.55 * min(s, 1.0)
    return max(base * drop * MOTORS["efficiency"], base * 0.18)

def line_pull_capacity_n(speed_mps: float):
    return available_torque_nm(speed_mps) / spool_radius

def solve_tensions(position, velocity, accel):
    px, py, pz = position["x"], position["y"], position["z"]
    vx, vy, vz = velocity["x"], velocity["y"], velocity["z"]
    axv, ayv, azv = accel["x"], accel["y"], accel["z"]
    mass = RIG["carriage_mass_kg"] + RIG["payload_mass_kg"]
    fx = mass*axv + RIG["cable_drag_coeff"]*vx
    fy = mass*ayv + RIG["cable_drag_coeff"]*vy
    fz = mass*azv + mass*RIG["gravity"] + RIG["cable_drag_coeff"]*vz
    dirs, lengths = {}, {}
    for k, (ax, ay, az) in anchors.items():
        u, L = unit_vec(ax, ay, az, px, py, pz)
        dirs[k] = u
        lengths[k] = L
    uz = {k: max(dirs[k][2], 1e-4) for k in dirs}
    total_uz = sum(uz.values())
    base = {k: (fz*uz[k]/total_uz)/max(uz[k],1e-4) for k in uz}
    sx = sum(dirs[k][0] for k in dirs)
    sy = sum(dirs[k][1] for k in dirs)
    tensions = base.copy()
    for k in tensions:
        tensions[k] += (fx*dirs[k][0]/(sx if abs(sx)>1e-6 else 1.0))*0.25
        tensions[k] += (fy*dirs[k][1]/(sy if abs(sy)>1e-6 else 1.0))*0.25
        tensions[k] = max(tensions[k], 0.5)
    return tensions, lengths, dirs

def motor_metrics(position, velocity, accel):
    speed = vec_len(velocity["x"], velocity["y"], velocity["z"])
    tensions, lengths, dirs = solve_tensions(position, velocity, accel)
    current_limit = drv8825_current_limit()
    torque_avail = available_torque_nm(speed)
    line_pull = line_pull_capacity_n(speed)
    per_motor = {}
    overload = False
    hottest = 35.0
    for k in tensions:
        line_force = tensions[k]
        torque_need = line_force * spool_radius
        current_est = current_limit * min(torque_need/max(torque_avail,1e-6), 1.15)
        margin = torque_avail / max(torque_need, 1e-6)
        temp_est = 35.0 + 32.0*min(current_est/max(current_limit,1e-6), 1.4)
        hottest = max(hottest, temp_est)
        if torque_need > torque_avail:
            overload = True
        per_motor[k] = {
            "tension_n": line_force,
            "torque_need_nm": torque_need,
            "torque_avail_nm": torque_avail,
            "current_est_a": current_est,
            "current_limit_a": current_limit,
            "margin": margin,
            "temp_est_c": temp_est,
            "line_pull_capacity_n": line_pull,
        }
    return {
        "speed_mps": speed,
        "current_limit_a": current_limit,
        "available_torque_nm": torque_avail,
        "overload": overload,
        "hottest_temp_c": hottest,
        "motors": per_motor,
    }
