# SpiderPi Hardware Build Guide

## Architecture

SpiderPi is a four-cable parallel robot (cable-driven parallel robot, CDPR) inspired by
stadium Spidercam systems. Four winches at the corners of a square frame control cable
lengths to position a suspended carriage anywhere in the working volume.

## System Components

- **Frame**: 2020 aluminum extrusion, square layout
- **Winches**: 4x NEMA 17 steppers + DRV8825 drivers
- **Carriage**: Lightweight 3D-printed plate with camera mount
- **Controller**: Raspberry Pi 4B running FastAPI + pigpio
- **Dashboard**: React + Three.js frontend (browser-based)
- **Communication**: WebSocket for real-time control

## Recommended Baseline Dimensions

| Parameter | Value | Notes |
|-----------|-------|-------|
| Frame footprint | 2.0 x 2.0 m | Use room_2m profile |
| Anchor height | 1.5 m | All four anchors at same height |
| Working volume | 1.6 x 1.6 x 1.0 m | Conservative bounds |
| Carriage mass | 300–500 g | Keep as light as possible |
| Cable diameter | 0.8–1.0 mm | Dyneema/Spectra braid |
| Spool radius | ~11 mm | Measure after installation |

## Frame Assembly

### Step 1: Cut extrusion
- 4x horizontal top rails: 2000 mm each
- 4x vertical corner posts: 1500 mm each
- 4x diagonal braces: cut to fit

### Step 2: Assemble corners
- Use corner brackets and M5 T-nuts
- Square the frame carefully — asymmetry creates positioning error
- Verify diagonals are equal before final tightening

### Step 3: Mount winches
- Attach corner motor mounts at each top corner
- Mount NEMA 17 motors with shafts pointing inward
- Install spools on motor shafts (use set screws + thread locker)

### Step 4: Install limit switches
- Mount one switch per winch at fully-wound reference position
- Use normally-closed (NC) wiring for fail-safe behavior
- Add pull-up resistors or use internal Pi pull-ups

### Step 5: Build carriage
- 3D-print or laser-cut lightweight baseplate
- Install 4 cable eyelet anchors at corners
- Mount camera or dummy weight at center
- Target mass: under 400 g total

### Step 6: String cables
- Route one Dyneema cable from each spool to carriage eyelet
- Use identical termination method on all four corners
- Pre-tension cables evenly before any power-on

## Electronics Wiring

### Power architecture
- Pi powered by official 5V 3A USB-C PSU
- Motors powered by separate 12V 5A PSU
- Shared ground between Pi and motor PSU
- NEVER power motors from Pi GPIO rails

### DRV8825 wiring (per motor)
| DRV8825 pin | Connection |
|-------------|-----------|
| VMOT | 12V PSU+ |
| GND (power) | 12V PSU- (shared ground) |
| STEP | Pi GPIO STEP pin |
| DIR | Pi GPIO DIR pin |
| EN | Pi GPIO EN pin (shared) |
| A1, A2 | Motor coil A |
| B1, B2 | Motor coil B |
| M0, M1, M2 | Microstepping config (1/16 = all HIGH) |

### GPIO pin assignment
| Axis | STEP | DIR | EN |
|------|------|-----|----|
| A | GPIO 12 | GPIO 5 | GPIO 6 |
| B | GPIO 13 | GPIO 16 | GPIO 6 |
| C | GPIO 19 | GPIO 20 | GPIO 6 |
| D | GPIO 26 | GPIO 21 | GPIO 6 |

### Limit switch wiring
| Axis | GPIO | Wiring |
|------|------|--------|
| A | GPIO 17 | NC to GND, pull-up |
| B | GPIO 27 | NC to GND, pull-up |
| C | GPIO 22 | NC to GND, pull-up |
| D | GPIO 23 | NC to GND, pull-up |
| E-stop | GPIO 24 | NC to GND, pull-up |

## DRV8825 Current Limit Setting

Formula: **I_limit = VREF × 2**

For 1.7A NEMA17 motors, set conservatively:
- Start at VREF = 0.6V → I_limit = 1.2A
- Adjust up slowly while monitoring temperature
- Maximum safe: VREF = 0.85V → I_limit = 1.7A (needs heatsink + airflow)

## Software Bring-up Sequence

1. Start in simulator mode on MacBook (no Pi needed)
2. Verify 3D scene, controls, and WebSocket work
3. Move to Raspberry Pi with same backend
4. Set SPIDERPI_SIM_GPIO=0 to enable real GPIO
5. Test one motor at a time (one-axis jog)
6. Verify limit switch polarity
7. Run calibration wizard step by step
8. Test slow multi-axis moves
9. Gradually increase speed to configured maximum

## Safety Rules

- Never test with people under the rig
- Always mount E-stop within reach
- Start with dummy weight, not real camera
- Use NC limit switches (fail-safe)
- Keep maximum speed conservative (0.3 m/s to start)
- Latch all faults until manually reset
- Never bypass E-stop circuit for testing
