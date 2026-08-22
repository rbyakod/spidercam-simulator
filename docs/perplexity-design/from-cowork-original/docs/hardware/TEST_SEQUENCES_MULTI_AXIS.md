# SpiderPi Multi-Axis Test Sequences

Run these tests in order. Do not advance to the next test until the current one passes.

## Test 1: Single Axis Sanity (run per axis, one at a time)

Command: POST /move {x:1.1, y:1.0, z:0.9, speed:0.1} (moves primarily axis A and B)
Expected: motor moves, cable length changes, no faults
Pass: carriage moves, telemetry shows new position, status returns idle

## Test 2: Opposite Pair Symmetry

Move to (0.5, 1.0, 0.9) then (1.5, 1.0, 0.9) at 0.1 m/s
Expected: symmetric motion left-to-right, equal cable length changes on A/C vs B/D
Pass: movement is smooth, no oscillation, position error less than 20mm

## Test 3: Z Collective Move

Move from z=0.9 to z=0.5 and back, holding XY constant
Expected: all four cables lengthen equally on descent
Pass: carriage descends vertically, no lateral drift

## Test 4: Micro-Square Path

Run square path with size=0.3m at z=0.9, speed=0.15 m/s
Expected: simulator shows square trail, real carriage traces square
Pass: corners are sharp, side lengths match within 30mm

## Test 5: Micro-Circle Path

Run circle path with radius=0.2m at z=0.9, speed=0.15 m/s
Expected: smooth circular motion, no jerking
Pass: path is visually circular, no missed steps audible

## Test 6: Diagonal Sweep

Run diagonal path from bounds corner to corner
Expected: straight-line motion diagonally across working volume
Pass: trail shows straight line in 3D view

## Test 7: Repeatability Test

Command center (1.0, 1.0, 0.9) 5 times, return to front-left each time
Expected: carriage returns to same position each time
Pass: position repeatability within 15mm (open-loop expectation)

## Test 8: Speed Ramp Test

Increase max_speed_mps from 0.15 to 0.3 to 0.5 in steps
Expected: motion stays smooth, no step loss at each speed
Pass: no audible step skipping, physics panel shows no overload

## Test 9: Simulator Parity Check

Compare trail in simulator with physical carriage path
Expected: shapes match within 5-10% of total path length
Pass: simulator is useful as planning tool for physical rig
