# SpiderCAM Spool Design Specification

## Key Geometry
- Barrel diameter: 40mm
- At 1/16 microstepping with 200-step motor: 3200 steps/rev
- Barrel circumference: pi x 40mm = 125.66mm per revolution
- Steps per metre: 3200 / 0.12566 = 25,466 steps/m

## Print Settings
- Material: PETG (preferred) or ABS
- Layer height: 0.2mm
- Infill: 40% gyroid
- Perimeters: 4
- No supports needed

## Motor Shaft Interface
- D-shaft: Standard NEMA 17 output, 5mm
- Grub screw: M3 x 5mm, tighten to 0.3 Nm

## Load Calculations (1m frame, 0.5 kg payload)
- Max cable tension: approx 14 N per cable
- At barrel radius 20mm: torque = 14N x 0.02m = 0.28 Nm
- NEMA 17 at 42Ncm = 0.42 Nm holding torque
- Safety factor: 0.42 / 0.28 = 1.5x
