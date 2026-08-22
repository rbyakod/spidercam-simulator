# SpiderPi Spool Design Specification

## Critical Parameter: Effective Spool Radius

The effective spool radius determines how many motor steps move the cable 1 meter.
Steps per meter = (motor_steps_per_rev x microsteps) / (2 x pi x spool_radius_m)
For 200 steps/rev, 16 microsteps, 11mm radius: 3640 steps/meter

Measuring procedure:
1. Mark spool with tape
2. Command exactly 20 full revolutions (200 steps x 20 = 4000 steps at full step)
3. Measure actual cable travel in mm
4. Effective radius = travel_mm / (20 x 2 x pi) mm
5. Enter in simulator config as spool_radius_m

## Baseline Design

Barrel diameter: 18mm, radius = 9mm (plus ~2mm line wrap = ~11mm effective)
Flange diameter: 28mm minimum
Flange thickness: 2.5mm each side
Barrel width: 14mm (fits about 15 wraps of 0.8mm line per layer)
Hub height: 8mm for set screw depth
Shaft bore: 5.0mm with 0.5mm flat for D-shaft

## Material Recommendations

PETG: recommended for temperature resistance and layer adhesion
ABS: acceptable but requires enclosure during print
PLA: acceptable for low-speed testing only (softens near 60C motor heat)

## Print Settings

Layer height: 0.2mm
Infill: 40% minimum (gyroid or honeycomb)
Walls: 4 perimeters minimum
Print orientation: flat side down

## Fit Tolerances

Shaft bore: print at 4.8mm, test fit, adjust
Set screw boss: use M3 heat-set insert or self-tap with M3 screw
All four spools must have identical barrel diameter

## NEMA17 Shaft Compatibility

Standard NEMA17 shaft: 5mm diameter, 20-24mm length, D-flat at 4.5mm
Coupler alternative: use 5mm rigid shaft coupler if direct fit is loose
