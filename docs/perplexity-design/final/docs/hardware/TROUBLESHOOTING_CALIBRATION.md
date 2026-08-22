# SpiderCAM Calibration Troubleshooting

## Problem: Offsets are very large (>100mm)
Causes: Frame dimensions in config do not match physical frame.
Fix: Re-measure physical frame, update FRAME_WIDTH/HEIGHT/DEPTH env vars, restart backend.

## Problem: Calibration says OK but position is wrong
Causes: Cable stretch, spool runout, cable slipped on spool.
Fix: Use stainless steel wire rope, check spool concentricity.

## Problem: One cable always reads zero tension
Causes: Cable is slack (gravity pulling camera asymmetrically).
Fix: Move camera toward affected corner to tension that cable.

## Problem: Homing fails on one axis
Causes: Limit switch wiring issue, wrong GPIO pin, DRV8825 fault.
Fix:
1. Press limit switch manually - verify GPIO reads LOW
2. Cross-reference WIRING_TABLE.md
3. Check DRV8825 FAULT pin (active LOW when fault)

## Problem: Accuracy degrades over time
Causes: Thermal expansion, cable creep, motor losing steps.
Fix:
1. Recalibrate after system reaches operating temperature
2. Use wire rope not synthetic rope
3. Reduce max_speed to prevent step losses
