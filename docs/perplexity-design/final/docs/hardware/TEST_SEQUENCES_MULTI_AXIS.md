# SpiderCAM Multi-Axis Test Sequences

## Test 1: Single-Axis Jog Verification
For each axis 0-3:
    POST /api/jog {"axis": 0, "distance": 0.05, "speed": 0.05}
    -> Verify movement in +X direction, then return with -0.05

## Test 2: Square Path
Waypoints: (0.2,0.8,0.2) -> (0.8,0.8,0.2) -> (0.8,0.8,0.8) -> (0.2,0.8,0.8) -> (0.2,0.8,0.2)
Use UI: Paths > Run > "square"
Check: No cable slack, smooth deceleration at corners.

## Test 3: Diagonal Speed Test
(0.1, 0.9, 0.1) -> (0.9, 0.7, 0.9), distance: 1.132m
At 0.3 m/s: approx 4.0 sec

## Test 4: Extreme Position Stress Test
Move to 8 workspace corners (0.1m margin). Note: low Y positions may show cable slack.

## Test 5: Endurance Run (30 minutes)
Loop square path. Check every 5 minutes:
- DRV8825 temperature (< 70 C)
- Position accuracy (< 5mm drift)
- Cable tension (all visually taut)
- No fault events in UI

## Test 6: Emergency Stop Recovery
1. Start moving to far position
2. Click E-STOP - verify stops within 0.5 seconds
3. Click Clear Faults - verify recovery
