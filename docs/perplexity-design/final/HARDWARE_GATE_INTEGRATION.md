# SpiderCAM Hardware Gate Integration

## Gate Sequence

1. HOMING GATE (homing_monitor.py)
   Blocks all move commands until all_homed == True

2. CALIBRATION GATE (calibration_gates.py)
   Soft gate - warns but does not block if skipped

3. SAFE MOTION GATE (safe_motion.py)
   Hard gate - blocks moves outside workspace or with bad tensions

## API Gate Responses

Move before homing:
    POST /api/move -> 400 {"detail": "Machine not homed - run homing sequence first"}

Move outside workspace:
    POST /api/move -> 400 {"detail": "Target [-0.5, 0.5, 0.5] is outside workspace"}

## Adding Custom Gates

    def my_gate() -> tuple:
        if my_condition:
            return False, "Condition not met"
        return True, "OK"
