# SpiderCAM Build Guide

## 1. Frame Assembly
Materials: 8x 1m lengths of 20x20mm aluminium extrusion, corner brackets, M5 T-nuts and bolts.

1. Assemble a rectangular box frame using corner brackets
2. Ensure frame is square using diagonal measurements (both diagonals must match)
3. Tighten all bolts to 2 Nm

## 2. Motor Mounting
1. Print 4x corner motor mounts from cad/corner_motor_mount_v1.scad (PETG, 40% infill)
2. Mount motors at the 4 top corners of the frame
3. Align motor shaft horizontally, pointing inward
4. Torque M3 bolts to 0.5 Nm

## 3. Spool Installation
1. Print 4x spools from cad/spool_v1_direct_5mm.scad
2. Press-fit spool onto motor shaft (D-flat alignment)
3. Check spool runs true (less than 0.5mm runout)

## 4. Cable Rigging
1. Thread 1.5mm wire rope through each spool groove
2. Route cable diagonally to centre of frame
3. Terminate with thimble and cable clamp at camera mount

## 5. Electronics Assembly
See WIRING_TABLE.md for all GPIO connections.

1. Mount Raspberry Pi and DRV8825 boards
2. Connect DRV8825 STEP/DIR/EN to RPi GPIO per wiring table
3. Connect stepper motors to DRV8825 (A1/A2/B1/B2)
4. Connect 12V SMPS to DRV8825 VM and GND
5. Connect limit switches to GPIO pins (INPUT_PULLUP)
6. Power RPi via USB-C (separate from motor supply)

## 6. Software Installation
See RUNBOOK.md for complete setup instructions.
