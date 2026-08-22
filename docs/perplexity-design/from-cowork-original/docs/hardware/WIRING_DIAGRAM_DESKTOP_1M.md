# SpiderPi Wiring Diagram - Desktop 1m Profile

## Frame Layout (top view, 1m x 1m)

    A (GPIO12/5) ------- B (GPIO13/16)
    |                           |
    |         CARRIAGE          |
    |            O              |
    |                           |
    D (GPIO26/21) ------- C (GPIO19/20)

## GPIO Assignment for Desktop 1m

| Axis | Step | Dir | Limit Switch |
|------|------|-----|--------------|
| A (front-left) | GPIO 12 | GPIO 5 | GPIO 17 |
| B (front-right) | GPIO 13 | GPIO 16 | GPIO 27 |
| C (rear-right) | GPIO 19 | GPIO 20 | GPIO 22 |
| D (rear-left) | GPIO 26 | GPIO 21 | GPIO 23 |
| E-Stop | - | - | GPIO 24 |
| EN (shared) | GPIO 6 | - | - |

## Power Distribution

12V PSU+ -> DRV8825 VMOT on all 4 boards
12V PSU- -> DRV8825 GND on all 4 boards
Pi GND -> same rail as 12V PSU- (shared ground)
Pi 5V/USB-C -> separate Pi PSU only
Pi 3.3V -> DRV8825 M0/M1/M2 (microstepping config)

## DRV8825 Board Layout (per driver)

    3.3V --[M0]--[M1]--[M2]-- (all HIGH = 1/16 step)
    GPIO --[STEP]
    GPIO --[DIR]
    GPIO --[EN]  (active LOW to enable)
    [GND] -- Pi GND and PSU GND joined here

## Safety Connections

NC limit switch: GPIO pin -> 10k pullup resistor -> 3.3V
                 GPIO pin -> 100nF cap -> GND
                 Switch NC contact: GPIO pin to GND
E-stop: same wiring as limit switch on GPIO 24
