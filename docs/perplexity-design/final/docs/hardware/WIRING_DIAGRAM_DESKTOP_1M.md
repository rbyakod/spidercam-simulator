# SpiderCAM Desktop 1m Frame - Wiring Diagram

## System Overview

    12V 10A SMPS -> VM on all 4x DRV8825 (motor power)
    RPi 4B GPIO  -> STEP/DIR/EN on all 4x DRV8825 (logic)
    DRV8825 A1/A2/B1/B2 -> NEMA 17 coil pairs

## RPi 4B Pin Connections

    Pin 7  (GPIO4)  -> FL Limit Switch (INPUT_PULLUP, switch to GND)
    Pin 11 (GPIO17) -> FL STEP
    Pin 12 (GPIO18) -> FL DIR
    Pin 13 (GPIO27) -> FL EN (active LOW)
    Pin 15 (GPIO22) -> FR STEP
    Pin 16 (GPIO23) -> FR DIR
    Pin 18 (GPIO24) -> FR EN
    Pin 22 (GPIO25) -> FR Limit Switch
    Pin 29 (GPIO5)  -> RL STEP
    Pin 31 (GPIO6)  -> RL DIR
    Pin 32 (GPIO12) -> RL Limit Switch
    Pin 33 (GPIO13) -> RL EN
    Pin 35 (GPIO19) -> RR STEP
    Pin 36 (GPIO16) -> RR Limit Switch
    Pin 37 (GPIO26) -> RR DIR
    Pin 40 (GPIO21) -> RR EN

## Motor Wiring (NEMA 17 4-wire)
Use multimeter continuity test to identify coil pairs.
Connect one coil to A1/A2 and the other to B1/B2.

## Cable Routing
- Keep signal wires away from motor power wires
- Use twisted pair for STEP/DIR signals over 30cm
- Ground the frame extrusion to SMPS chassis GND
