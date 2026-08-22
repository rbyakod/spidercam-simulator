# SpiderPi Calibration Checklist

## 1. Frame Sizing and Profile

- [ ] Select machine profile in dashboard (desktop_1m, room_1p5m, or room_2m)
- [ ] Apply profile and verify anchor coordinates match physical frame
- [ ] Confirm spool radius setting matches measured spool
- [ ] Check bounds are within physical frame dimensions

## 2. Visual Geometry Check

- [ ] View 3D scene - cables should point to correct corners
- [ ] Move to center position in simulator and confirm shape looks correct
- [ ] Verify cable lengths update correctly in telemetry panel

## 3. Wiring and I/O Check

- [ ] All limit switches read idle (not triggered) at rest
- [ ] E-stop button reads correct idle state
- [ ] Motor enable signal activates (motors hold) when enabled
- [ ] All four axes show expected direction when manually moved

## 4. Motor Direction Verification

- [ ] Axis A: jog +10 steps, cable winds in (gets shorter)
- [ ] Axis B: jog +10 steps, cable winds in
- [ ] Axis C: jog +10 steps, cable winds in
- [ ] Axis D: jog +10 steps, cable winds in
- [ ] Mark all directions as verified in Calibration Wizard

## 5. Homing All Axes

- [ ] Home axis A: switch triggers and position resets to zero
- [ ] Home axis B: switch triggers and position resets to zero
- [ ] Home axis C: switch triggers and position resets to zero
- [ ] Home axis D: switch triggers and position resets to zero

## 6. Spool Radius Calibration

- [ ] Mark each spool with tape marker
- [ ] Command exactly 20 revolutions (3200 steps at 1/16 microstep)
- [ ] Measure cable travel distance for each spool
- [ ] Calculate radius = travel / (20 x 2 x pi)
- [ ] Enter measured radius in dashboard and save config
- [ ] Verify all four spools have matching radius (within 0.5mm)

## 7. Center and Zero Calibration

- [ ] Command carriage to logical center (1.0, 1.0, 0.9)
- [ ] Physically confirm carriage is visually centered
- [ ] Record actual cable lengths at this position
- [ ] Save zero offsets to config

## 8. Bounds Verification

- [ ] Move to front-left corner at 0.1 m/s
- [ ] Move to front-right corner at 0.1 m/s
- [ ] Move to rear-left corner at 0.1 m/s
- [ ] Move to rear-right corner at 0.1 m/s
- [ ] Verify no mechanical interference at any extreme
- [ ] Test E-stop during motion - carriage must stop immediately
- [ ] Save verified bounds to config

## 9. Path Validation

- [ ] Run square path at 0.15 m/s and verify shape
- [ ] Run circle path at 0.15 m/s and verify shape
- [ ] Run diagonal sweep and verify smooth motion
- [ ] Mark both paths as passed in dashboard

## 10. Acceptance

- [ ] All checklist items above marked complete
- [ ] Save machine profile with verified settings
- [ ] Create named profile for this build variant
- [ ] Document spool radius, zero lengths, and bounds in notes
