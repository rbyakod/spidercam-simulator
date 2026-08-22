# SpiderPi Manufacturing Release Checklist

## v0.1-desktop (1m x 1m desktop prototype)

### Frame
- [ ] All four extrusion lengths cut to 1000mm +/- 1mm
- [ ] Frame is square: diagonals equal within 2mm
- [ ] Corner brackets tight, no flex under hand pressure
- [ ] Motor mounts flush to extrusion face

### Spools
- [ ] All four spools printed from same STL file
- [ ] Spool barrel diameters measured: all within +/- 0.3mm of each other
- [ ] Set screws tight on motor shafts with thread locker
- [ ] 20-turn measurement performed, radius recorded

### Electronics
- [ ] All DRV8825 boards installed with heatsinks
- [ ] VREF set to 0.6V on all four boards
- [ ] All GPIO signals verified with multimeter before power-on
- [ ] Limit switches tested in isolation before mounting
- [ ] E-stop circuit verified: pressing stop halts all motion

### Software
- [ ] Simulator runs on MacBook and matches physical geometry
- [ ] Backend runs on Pi, API reachable from MacBook
- [ ] All calibration wizard steps completed
- [ ] machine_profiles.yaml updated with desktop_1m verified settings
- [ ] Named profile saved: desktop_1m_v0.1

### Acceptance Test
- [ ] Square path at 0.15 m/s completes without fault
- [ ] E-stop test: press during motion, carriage stops within 50mm
- [ ] Limit switch test: trigger each switch manually, fault latches
- [ ] 10-minute continuous path run without overheating

## v0.2-room (1.5m or 2m room installation)

All items from v0.1 plus:

### Frame
- [ ] Frame anchored to ceiling/wall with safety cable backup
- [ ] Weight test: hang 2x max carriage weight for 1 hour
- [ ] All cable routing checked for abrasion points

### Performance
- [ ] Repeatability test: 10-point return to center, error < 15mm
- [ ] Thermal test: 30-minute run, driver temp < 75C
- [ ] Camera test: Pi camera streaming over MJPEG or WebRTC

### Documentation
- [ ] As-built anchor coordinates measured and saved
- [ ] Spool radii and zero lengths documented
- [ ] Config YAML exported and archived
