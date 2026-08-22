# SpiderPi Wiring Table

## Pi GPIO Header Map (BCM numbering)

| BCM | Physical | Function | Connects to |
|-----|----------|----------|-------------|
| 12 | Pin 32 | STEP A | DRV8825 A STEP |
| 5 | Pin 29 | DIR A | DRV8825 A DIR |
| 6 | Pin 31 | EN shared | All DRV8825 EN |
| 13 | Pin 33 | STEP B | DRV8825 B STEP |
| 16 | Pin 36 | DIR B | DRV8825 B DIR |
| 19 | Pin 35 | STEP C | DRV8825 C STEP |
| 20 | Pin 38 | DIR C | DRV8825 C DIR |
| 26 | Pin 37 | STEP D | DRV8825 D STEP |
| 21 | Pin 40 | DIR D | DRV8825 D DIR |
| 17 | Pin 11 | LIMIT A | Switch A NC to GND |
| 27 | Pin 13 | LIMIT B | Switch B NC to GND |
| 22 | Pin 15 | LIMIT C | Switch C NC to GND |
| 23 | Pin 16 | LIMIT D | Switch D NC to GND |
| 24 | Pin 18 | E-STOP | E-stop button NC to GND |
| GND | Multiple | Signal GND | Common ground |

## DRV8825 Microstepping Config for 1/16 step
Set M0=HIGH, M1=HIGH, M2=HIGH on all four DRV8825 boards.
Connect each M pin to Pi 3.3V rail.

## Limit Switch Wiring
NC contact between GPIO pin and GND.
Pi internal pull-up enabled in software.
Add 100nF capacitor between GPIO and GND for hardware debounce.

## Current Limit Formula
I_limit = VREF x 2
Start at VREF=0.6V giving 1.2A limit.
Add heatsink before raising above 0.75V.
