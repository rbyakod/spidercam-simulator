# SpiderPi Calibration Troubleshooting Guide

## Motor Direction Problems

Symptom: cable gets longer when it should get shorter
Cause: motor direction inverted
Fix: toggle invert_dir in config for that axis, or swap motor coil pair A1/A2

Symptom: one motor correct, another inverted
Cause: inconsistent wiring between DRV8825 boards
Fix: check DIR pin for each motor, use invert_dir per-axis in config

## Homing Problems

Symptom: home command runs, motor moves, switch not found
Cause: switch wired wrong or motor seek direction inverted
Fix: verify switch triggers (LED if available), check direction first

Symptom: switch found but position does not reset to zero
Cause: homing monitor not marking axis as homed
Fix: call POST /wizard/homed with {axis, homed: true} after physical verification

Symptom: switch triggers immediately (false positive)
Cause: noise on GPIO line, switch wired NO instead of NC
Fix: add 100nF capacitor; rewire switch in NC configuration

## Spool Radius Problems

Symptom: commanded 1m move, carriage moves 0.8m
Cause: spool radius in config is too small
Fix: increase spool_radius_m by ratio (actual/commanded)

Symptom: position drifts after many moves
Cause: spool radius calibration error accumulated over steps
Fix: re-run 20-turn measurement, recalibrate radius

Symptom: different spools produce different travel per step
Cause: spools are not identical diameter
Fix: re-print spools from same CAD file, measure each one

## Position Accuracy Problems

Symptom: carriage reaches commanded position but is off by 5-10cm
Cause: anchor coordinates in config do not match physical positions
Fix: measure physical anchor positions carefully, update config

Symptom: carriage drifts over time with no commanded move
Cause: missed steps, cable stretch, or thermal expansion
Fix: re-home and re-calibrate; reduce speed and acceleration

## Cable Problems

Symptom: one cable goes slack during motion
Cause: that corner cable is not maintaining tension
Fix: check carriage mass balance; increase minimum tension in physics config

Symptom: cables overlap on spool
Cause: cable enters spool at wrong angle
Fix: add cable guide or pulley to redirect cable tangentially to spool

## Dashboard/WebSocket Problems

Symptom: dashboard shows disconnected
Cause: backend not running or port blocked
Fix: verify uvicorn is running, check VITE_WS_URL environment variable

Symptom: 3D scene shows cable going to wrong corner
Cause: anchor coordinate X/Y may be swapped
Fix: verify A is front-left, B is front-right in your physical layout

## Motor Overload Warnings

Symptom: physics panel shows overload
Cause: speed too high or carriage too heavy for motor spec
Fix: reduce max_speed_mps; reduce carriage mass; increase DRV8825 VREF

Symptom: motors getting hot (over 60C)
Cause: current limit too high or motors running at near-max load
Fix: reduce VREF; add heatsinks; improve airflow; reduce acceleration
