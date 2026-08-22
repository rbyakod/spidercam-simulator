# SpiderCAM Real Hardware Bring-Up Guide

## Step 1: Set DRV8825 Current Limits
BEFORE powering motors, set Vref = I_limit x 0.5
For NEMA 17 at 1.5A: Vref = 0.75V. Measure at trim pot wiper.

## Step 2: Single Axis Motor Test
1. Connect ONE motor to FL DRV8825
2. Start backend: uvicorn main:app --reload --port 8000
3. Jog FL axis +5cm in UI
4. Verify motor turns smoothly. If reversed, swap A1/A2 or B1/B2 wires.
5. Repeat for all 4 axes

## Step 3: Limit Switch Test
1. Manually press each limit switch
2. Check fault LED activates in UI
3. Clear fault and verify recovery

## Step 4: First Homing Run
1. Ensure cables have some slack
2. Click "Run Homing Sequence"
3. All 4 axes should show green "Homed" badge

## Step 5: First Move
Target: X=0.5, Y=0.8, Z=0.5. All 4 cables must remain taut.

## Step 6: Calibration
Follow CALIBRATION_CHECKLIST.md.

## Common Issues

| Symptom              | Likely Cause           | Fix                          |
|----------------------|----------------------|------------------------------|
| Motor vibrates, no turn | Current too low    | Increase Vref                |
| Motor overheating    | Current too high       | Decrease Vref                |
| Motor loses steps    | Speed too high         | Reduce max_speed             |
| Cable goes slack     | Wrong frame dimensions | Check config                 |
| Limit not detected   | Wrong GPIO pin         | Check WIRING_TABLE.md        |
