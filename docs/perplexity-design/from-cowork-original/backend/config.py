FRAME = {
    "anchors": {
        "A": [0.0, 0.0, 1.5],
        "B": [2.0, 0.0, 1.5],
        "C": [2.0, 2.0, 1.5],
        "D": [0.0, 2.0, 1.5],
    },
    "bounds": {
        "x": [0.2, 1.8],
        "y": [0.2, 1.8],
        "z": [0.3, 1.3],
    },
    "spool_radius_m": 0.011,
    "motor_steps_per_rev": 200,
    "microsteps": 16,
}
MOTORS = {
    "rated_current_a": 1.7,
    "holding_torque_nm": 0.42,
    "phase_resistance_ohm": 1.5,
    "phase_inductance_mh": 3.2,
    "supply_voltage": 12.0,
    "drv8825_vref": 0.75,
    "drv8825_rsense": 0.1,
    "efficiency": 0.82,
    "safe_temp_c": 85.0,
}
RIG = {
    "carriage_mass_kg": 0.40,
    "payload_mass_kg": 0.08,
    "gravity": 9.81,
    "cable_drag_coeff": 0.08,
    "max_speed_mps": 0.7,
    "max_accel_mps2": 0.9,
}
