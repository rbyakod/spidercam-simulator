# Hardware Gate Integration Guide

## Overview

The calibration wizard uses hardware gates to auto-complete steps
when real hardware state confirms the required conditions.

## Gate Sources

| Gate | Source | How to trigger |
|------|--------|----------------|
| profile_loaded | load_config() returns valid config | Apply any machine profile |
| all_directions_ok | homing_monitor.axis_direction_ok | POST /wizard/motor-direction for each axis |
| all_homed | homing_monitor.axis_homed | POST /wizard/homed for each axis after homing |
| spool_radius_measured | homing_monitor.spool_radius_measured | POST /wizard/spool-radius with measured value |
| center_calibrated | homing_monitor.center_calibrated | POST /wizard/zero-lengths with measured lengths |
| bounds_verified | homing_monitor.bounds_verified | POST /wizard/bounds with confirmed values |
| switches_idle | hardware_rt.get_switch_states() all False | Physical switches at rest |
| path_square_ok | homing_monitor.path_square_ok | POST /paths/replay/square_demo runs without fault |
| path_circle_ok | homing_monitor.path_circle_ok | Similar for circle path |

## Simulator Mode

When SPIDERPI_SIM_GPIO=1 (default on Mac):
- switch states come from hardware_rt simulated values
- Use HardwareGatePanel in dashboard to simulate switch states
- Direction and homing gates must be set manually via wizard endpoints

## Hardware Mode

When SPIDERPI_SIM_GPIO=0 (Raspberry Pi with GPIO):
- switch states read directly from GPIO pins via pigpio
- limit_monitor callbacks trigger fault on switch event during motion
- Gate state updates automatically as hardware is configured

## Integration Points in main.py

handle_limit_event() is called by LimitMonitor on any switch change.
homing_monitor.mark_*() methods should be called from:
- HomingController.home_axis() on successful home
- Wizard endpoints after user confirms direction
- apply_position() after successful path completion
