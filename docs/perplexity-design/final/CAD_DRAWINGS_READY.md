# SpiderCAM CAD Drawings Status

## Available OpenSCAD Files

| File                           | Description              | Status         |
|-------------------------------|--------------------------|----------------|
| cad/spool_v1_direct_5mm.scad  | Direct 5mm D-shaft spool | Ready to print |
| cad/spool_v1_coupler.scad     | Coupler hub spool        | Ready to print |
| cad/corner_motor_mount_v1.scad| NEMA 17 corner mount     | Ready to print |

## Export STL

    openscad -o spool_direct.stl cad/spool_v1_direct_5mm.scad
    openscad -o spool_coupler.stl cad/spool_v1_coupler.scad
    openscad -o corner_mount.stl cad/corner_motor_mount_v1.scad

## Slicer Settings

| Parameter  | Spool | Motor Mount |
|------------|-------|-------------|
| Material   | PETG  | PETG/ABS    |
| Layer      | 0.2mm | 0.2mm       |
| Infill     | 40%   | 40%         |
| Perimeters | 4     | 4           |
| Supports   | None  | None        |
