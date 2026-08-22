# SpiderPi CAD Package - Ready to Print

## Files in cad/ directory

spool_v1_direct_5mm.scad
    Direct NEMA17 shaft mount spool (5mm D-shaft).
    Effective radius approximately 11mm after line wrapping.
    Print 4 identical copies.
    Use PETG or ABS. Do NOT use PLA for structural spools.

spool_v1_coupler.scad
    Alternative spool using shaft coupler.
    Use when direct shaft mount has too much play.

corner_motor_mount_v1.scad
    Corner mount for NEMA17 on 2020 extrusion.
    Mounts motor with shaft inward.
    Print 4 identical copies.

## Exporting to STL

1. Install OpenSCAD (free, openscad.org)
2. Open each .scad file
3. Press F6 to render fully
4. Export as STL: File > Export > Export as STL

## Exporting to STEP

1. Export STL from OpenSCAD
2. Import STL into FreeCAD
3. Use Part workbench: Part > Convert to Solid
4. Export as STEP: File > Export > STEP

## Critical Dimension Verification

After printing each spool:
1. Measure barrel diameter with calipers
2. All four spools must match within 0.5mm
3. Enter measured radius in simulator config
4. Re-run 20-turn calibration to verify

## Print Settings Summary

| Part | Material | Layer Height | Infill | Perimeters |
|------|----------|-------------|--------|------------|
| Spool | PETG | 0.2mm | 40% | 4 |
| Mount | PETG or PLA | 0.2mm | 30% | 3 |
