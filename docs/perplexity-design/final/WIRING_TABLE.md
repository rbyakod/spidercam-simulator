# SpiderCAM GPIO Wiring Table

## RPi 4B GPIO Pin Assignments

| Signal    | RPi GPIO | RPi Pin | Axis | DRV8825 Pin     |
|-----------|---------|---------|------|-----------------|
| FL STEP   | GPIO17  | Pin 11  | FL   | STEP            |
| FL DIR    | GPIO18  | Pin 12  | FL   | DIR             |
| FL ENABLE | GPIO27  | Pin 13  | FL   | EN (active LOW) |
| FR STEP   | GPIO22  | Pin 15  | FR   | STEP            |
| FR DIR    | GPIO23  | Pin 16  | FR   | DIR             |
| FR ENABLE | GPIO24  | Pin 18  | FR   | EN              |
| RL STEP   | GPIO5   | Pin 29  | RL   | STEP            |
| RL DIR    | GPIO6   | Pin 31  | RL   | DIR             |
| RL ENABLE | GPIO13  | Pin 33  | RL   | EN              |
| RR STEP   | GPIO19  | Pin 35  | RR   | STEP            |
| RR DIR    | GPIO26  | Pin 37  | RR   | DIR             |
| RR ENABLE | GPIO21  | Pin 40  | RR   | EN              |

## Limit Switches

| Axis | GPIO   | Pin    | Pull   |
|------|--------|--------|--------|
| FL   | GPIO4  | Pin 7  | PUD_UP |
| FR   | GPIO25 | Pin 22 | PUD_UP |
| RL   | GPIO12 | Pin 32 | PUD_UP |
| RR   | GPIO16 | Pin 36 | PUD_UP |

## IMPORTANT NOTES
1. NEVER connect/disconnect motors while powered
2. Set DRV8825 current limit BEFORE connecting motors
3. RPi GPIO is 3.3V logic - DRV8825 accepts 3.3V signals
4. Add heatsinks to all DRV8825 modules
5. Common GND: SMPS GND = RPi GND = DRV8825 GND
