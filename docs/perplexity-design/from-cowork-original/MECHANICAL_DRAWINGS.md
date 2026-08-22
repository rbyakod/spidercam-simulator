# SpiderPi Mechanical Drawings Reference

## Coordinate System

Origin (0,0,0) is at anchor A (front-left-top corner).
X axis runs front-to-back (A to B).
Y axis runs left-to-right (A to D).
Z axis is vertical (positive UP).

## room_2m Profile Dimensions

Frame footprint: 2000 x 2000 mm
Anchor height: 1500 mm above floor
Anchor positions:
    A = (0, 0, 1500) mm
    B = (2000, 0, 1500) mm
    C = (2000, 2000, 1500) mm
    D = (0, 2000, 1500) mm

Working volume:
    X: 200 to 1800 mm
    Y: 200 to 1800 mm
    Z: 300 to 1300 mm

## Frame Members (2020 extrusion)

Top ring: 4x 2000mm horizontal members
Corner uprights: 4x 1500mm vertical members
Cross-braces: 4x diagonal braces cut to fit (~2830mm per brace for 2m frame)

## Carriage Plate

Material: 3mm PETG or 4mm plywood
Outer dimension: 120 x 120 mm
Cable eyelet positions: 15mm from each corner
Central camera mount: M4 bolt pattern, 25mm circle

## Spool Design Parameters

Effective radius after line wrap: 11 +/- 0.5 mm
Flange outer diameter: 28-30 mm
Barrel width: 14 mm
Shaft bore: 5mm with flat for set screw
Material: PETG (preferred) or ABS

## Fabrication Tolerances

Anchor position accuracy: +/- 5 mm acceptable
Spool radius consistency: all four spools must match within +/- 0.5 mm
Cable routing: all cables must exit spool at same height

## Verification Procedure

Measure physical anchor distances after assembly.
Enter measured anchor coordinates in config.
Command carriage to center and measure actual position.
Adjust zero_lengths_m offsets until sim matches physical.
