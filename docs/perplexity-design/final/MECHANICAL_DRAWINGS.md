# SpiderCAM Mechanical Drawings and Dimensions

## Frame Specifications (default 1m x 1m x 1m)

    Top View:
    FL(0,1,0) -------- FR(1,1,0)
    |                          |
    |     Camera mount         |
    |     at (0.5, y, 0.5)     |
    |                          |
    RL(0,1,1) -------- RR(1,1,1)

## Anchor Points

| Corner | X (m) | Y (m) | Z (m) |
|--------|--------|--------|--------|
| FL     | 0.0    | 1.0    | 0.0    |
| FR     | 1.0    | 1.0    | 0.0    |
| RL     | 0.0    | 1.0    | 1.0    |
| RR     | 1.0    | 1.0    | 1.0    |

Y=1.0 means anchors are at the top of the frame.

## Spool Dimensions

| Parameter      | Direct 5mm | Coupler |
|---------------|-----------|---------|
| Flange dia    | 60mm      | 60mm    |
| Barrel dia    | 40mm      | 40mm    |
| Barrel width  | 20mm      | 20mm    |
| Cable grooves | 12        | 12      |

## Workspace Envelope
- Usable XZ workspace: 0.05m margin from each wall
- Effective workspace: 0.9m x 0.9m (for 1m frame)
- Optimal operating height Y: 0.7m - 0.9m
